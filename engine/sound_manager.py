from pyaudio import PyAudio, paFloat32


def interpolated_peak(alpha, beta, gamma):
    return 0.5 * (alpha - gamma) / (alpha - 2 * beta + gamma)


class SoundManager:
    def __init__(self) -> None:
        self.audio = PyAudio()

    def get_available_devices(self) -> list[str]:
        return list(
            map(
                lambda info: str(info["name"]),
                filter(
                    lambda info: int(info["maxInputChannels"]) > 0,
                    map(
                        self.audio.get_device_info_by_index,
                        range(self.audio.get_device_count()),
                    ),
                ),
            )
        )

    def connect(self, device_name: str, block_period: float = 0.25):
        devices = list(
            filter(
                lambda info: info["name"] == device_name,
                map(
                    self.audio.get_device_info_by_index,
                    range(self.audio.get_device_count()),
                ),
            )
        )
        if len(devices) == 0:
            raise ValueError(f"Device {device_name} not found")

        device = devices[0]
        sample_rate = int(device["defaultSampleRate"])
        length = int(block_period * sample_rate)

        stream = self.audio.open(
            rate=sample_rate,
            channels=1,
            format=paFloat32,
            input=True,
            output=False,
            input_device_index=int(device["index"]),
            frames_per_buffer=length,
        )

        # TODO: Need to somehow schedule a function to periodically read the
        # stream and process into the pitch's frequency.
        # Perhaps pyglet's `clock.schedule` family of methods would suffice?

    # def read_frequency(self, block: list[float])
