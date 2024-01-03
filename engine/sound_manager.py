from pyaudio import PyAudio, paContinue, paFloat32, Stream

import numpy as np
import scipy as sp


def interpolated_peak(alpha, beta, gamma):
    return 0.5 * (alpha - gamma) / (alpha - 2 * beta + gamma)


class SoundManager:
    window_size = 0.25

    _stream: Stream | None = None
    _buffer = bytes()
    _buffer_length = 0

    _frequency: float | None = None

    def __init__(self) -> None:
        self._audio = PyAudio()

    @property
    def frequency(self) -> float | None:
        return self._frequency

    def get_available_devices(self) -> list[str]:
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
        if in_data is not None:
            self._buffer += in_data
            self._buffer_length += frame_count

        if self._buffer_length > self._sample_rate * self.window_size:
            self._read_frequency(self._buffer)
            self._buffer = bytes()
            self._buffer_length = 0

        return (None, paContinue)

    def _read_frequency(self, block: bytes):
        window = np.frombuffer(block, dtype=np.float32)

        # Hamming Window
        signal = np.hamming(len(window)) * window

        # Zero Padding
        signal = np.pad(
            signal,
            [(0, int(0.5 * self._sample_rate) - len(signal))],
            mode="constant",
        )

        # Take Magnitude of Fourier Transform
        signal = np.fft.fft(signal)
        signal = np.abs(signal)

        # Harmonic Product Spectrum
        harmonics = 4  # TODO: Move to constant
        spectra = [
            sp.signal.resample(signal, len(signal) // n)
            for n in range(1, harmonics + 1)
        ]

        min_length = min(map(lambda s: len(s), spectra))
        # TODO: Surely this can be rewritten as a map
        cropped_spectra = np.zeros(
            (len(spectra), min_length),
            dtype=signal.dtype,
        )
        for i, s in enumerate(spectra):
            cropped_spectra[i] += s[:min_length]

        hps = np.prod(cropped_spectra, axis=0)

        # Crop start
        ignore = 0
        peak = np.argmax(hps[ignore: len(hps) // 2]) + ignore

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
            self._frequency = frequency
        else:
            self._frequency = None
        print(self.frequency)

    def connect(self, device_name: str):
        self.bytes = bytes()
        if self._stream is not None:
            self._stream.close()
            self._stream = None

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

        self._stream = self._audio.open(
            input=True,
            input_device_index=int(device["index"]),
            rate=self._sample_rate,
            # Read window in chunks as consistency is better this way:
            frames_per_buffer=2**10,
            channels=1,
            format=paFloat32,
            stream_callback=self._callback,
        )

    def __del__(self) -> None:
        if self._stream is not None:
            self._stream.close()
        self._audio.terminate()
