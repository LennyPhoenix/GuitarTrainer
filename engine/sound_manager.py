from pyaudio import PyAudio, paContinue, paFloat32, Stream
from pyglet.event import EventDispatcher
from pyglet import clock

import numpy as np
import scipy as sp

from .note import frequency_to_offset


def interpolated_peak(alpha, beta, gamma):
    """Quadratic interpolation of the peak of a parabola.

    This is used by the peak detection of the pitch tracker to ensure we get a
    precise enough reading.
    """
    return 0.5 * (alpha - gamma) / (alpha - 2 * beta + gamma)


class SoundManager(EventDispatcher):
    """Does all the heavy lifting of detecting the fundamental frequency of the
    user's microphone input.

    Settings are adjustable, but have been chosen as they work the best for my
    specific use-case. It might be helpful to make these adjustable from inside
    the application for better support on other devices.


    """

    # The minimum average magnitude of each frame for it to not be discorded
    noise_threshold: float = 0.1
    # The size of the sliding window in seconds
    window_size: float = 0.6
    # The target size to pad the sliding window to, also in seconds
    padded_size: float | None = 0.9
    # The total number of harmonics to work with in the harmonic product
    # spectrum
    harmonics: int = 4

    # Last broadcasted offset
    broadcasted_offset: int | None = None
    # Last detected offset
    last_offset: int | None = None
    last_offset_counter: int = 0

    _stream: Stream | None = None
    _buffer = bytes()
    _buffer_length = 0

    _frequency: float | None = None

    def __init__(self) -> None:
        # We need an instance of PyAudio to use it
        self._audio = PyAudio()

    @property
    def frequency(self) -> float | None:
        """The last frequency detected by pitch tracker."""
        return self._frequency

    def get_available_devices(self) -> list[str]:
        """Returns a list of all available input device names."""
        # 1. Get all device information
        # 2. Filter by devices with at least 1 input channel
        # 3. Map to just the name of each device
        return list(
            map(
                lambda info: str(info["name"]),
                filter(
                    lambda info: int(info["maxInputChannels"]) > 0,
                    map(
                        self._audio.get_device_info_by_index,
                        range(self._audio.get_device_count()),
                    ),
                ),
            )
        )

    def _callback(
        self,
        in_data: bytes | None,
        frame_count: int,
        _time_info,
        _status_flags,
    ) -> tuple[bytes | None, int]:
        """Called by PyAudio every time there is new audio data to read.

        `in_data` is the audio data being read, and the `frame_count` indicates
        the number of frames (specified as a 32-bit float) contained within.
        This is important as `in_data` is just bytes, so without knowing the
        datatype being used it is useless.
        """

        # This is the length we are aiming for in our sliding window
        target_length = int(self._sample_rate * self.window_size)

        # Checks we have actually been passed data
        if in_data is not None:
            # Convert from bytes to a numpy array
            window = np.frombuffer(in_data, dtype=np.float32)
            # If silent...
            if np.mean(np.abs(window)) < self.noise_threshold:
                # ...reset the buffer...
                self._buffer = bytes()
                self._buffer_length = 0
                self._frequency = None
            else:
                # ...otherwise, append to the buffer.
                self._buffer += in_data
                self._buffer_length += frame_count

        if self._buffer_length >= target_length:
            # We use a sliding window here, so we discord any extra audio data
            # from the front of the array. Newest data is appended to the back.
            # This way we get fast updates and keep using the latest data we
            # have received.
            self._buffer = self._buffer[-target_length * 4 :]
            self._buffer_length = target_length

            # Only read the frequency if the buffer is full.
            self._read_frequency(self._buffer)

        # We schedule this event instead of calling it directly as the callback
        # is running on a separate thread to our UI, so we need to make sure we
        # don't crash OpenGL by attempting to make graphics calls from another
        # thread.
        # Scheduling works here because it pushes the function call to a stack
        # on the main thread, where it is run later once the event loop is at
        # rest (usually about once per frame).
        clock.schedule_once(
            lambda _: self.dispatch_event(
                "on_frequency_change",
                self.frequency,
            ),
            0.0,
        )

        # Tell PyAudio to continue reading data.
        return (None, paContinue)

    def _read_frequency(self, block: bytes):
        """Converts some block of memory to a usable frequency."""

        # Read into numpy array
        window = np.frombuffer(block, dtype=np.float32)

        # Hamming Window
        signal = np.hamming(len(window)) * window

        # Zero Padding
        if self.padded_size is not None:
            signal = np.pad(
                signal,
                [(0, int(self.padded_size * self._sample_rate) - len(signal))],
                mode="constant",
            )

        # Take Magnitude of Fourier Transform
        signal = np.fft.fft(signal)
        signal = np.abs(signal)

        # Generate harmonic spectra
        spectra = [
            sp.signal.resample(signal, len(signal) // n)
            for n in range(1, self.harmonics + 1)
        ]

        # Crop to the lowest spectrum size
        target_length = min(map(len, spectra))
        cropped_spectra = np.array(list(map(lambda s: s[:target_length], spectra)))

        # Take HPS
        hps = np.prod(cropped_spectra, axis=0)

        # Crop start (Disabled)
        ignore = 0
        peak = np.argmax(hps[ignore : len(hps) // 2]) + ignore

        # Quadratic Interpolation
        alpha = signal[peak - 1]
        beta = signal[peak]
        gamma = signal[peak + 1]
        peak += interpolated_peak(alpha, beta, gamma)

        # Bin -> Frequency Conversion
        bin_size = self._sample_rate / len(signal)
        frequency = peak * bin_size

        # Anything below 20Hz is probably background noise
        if frequency > 20.0:
            self._frequency = float(frequency)
        else:
            self._frequency = None

    def connect(self, device_name: str):
        """Connects to an audio device by its name and starts listening for
        fundamentals."""

        # Clear existing connection
        self.bytes = bytes()
        if self._stream is not None:
            self._stream.close()
            self._stream = None

        # Get all devices matching passed name
        devices = list(
            filter(
                lambda info: info["name"] == device_name,
                map(
                    self._audio.get_device_info_by_index,
                    range(self._audio.get_device_count()),
                ),
            )
        )
        if len(devices) == 0:
            raise ValueError(f"Device {device_name} not found")

        device = devices[0]
        self._sample_rate = int(device["defaultSampleRate"])

        # Open audio stream with PyAudio
        self._stream = self._audio.open(
            input=True,
            input_device_index=int(device["index"]),
            rate=self._sample_rate,
            # Read window in chunks as consistency is better this way:
            frames_per_buffer=2**9,  # ~512 frames per buffer
            channels=1,
            format=paFloat32,
            stream_callback=self._callback,
        )

    def on_frequency_change(self, frequency: float | None):
        # Convert frequency to pitch
        if frequency is not None:
            offset = frequency_to_offset(frequency)
        else:
            offset = None

        # Increment counter if offset is the same as last offset
        if offset == self.last_offset:
            self.last_offset_counter += 1
        # Reset counter if offset is different from last offset
        else:
            self.last_offset = offset
            self.last_offset_counter = 0

        # Only broadcast to others if the offset has been the same for 5
        # frames, and is different from the last *broadcasted* offset.
        if (
            self.last_offset_counter >= 5
            and self.last_offset != self.broadcasted_offset
        ):
            self.broadcasted_offset = self.last_offset
            self.dispatch_event("on_new_offset", self.broadcasted_offset)

    def __del__(self) -> None:
        # Must cleanup when deleted
        if self._stream is not None:
            self._stream.close()
        self._audio.terminate()


SoundManager.register_event_type("on_frequency_change")
SoundManager.register_event_type("on_new_offset")
