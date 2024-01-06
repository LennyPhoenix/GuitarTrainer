import json
from os import environ, path, mkdir
from typing import TypedDict
from copy import deepcopy

from .instrument import Instrument
from .progress import Progress


class Config(TypedDict):
    input_device: str | None


DEFAULT_CONFIG: Config = {"input_device": None}


class ProgressData(TypedDict):
    string_progress: list[tuple[int | None, int | None]]
    highest_note: tuple[int | None, int | None]
    scales: dict[str, tuple[bool, bool] | None]


InstrumentData = list[ProgressData]


def gen_default_instrument(instrument: Instrument) -> InstrumentData:
    return [
        {
            "string_progress": [(None, None)] * len(instrument.value.strings),
            "highest_note": (None, None),
            "scales": {
                "major": None,
                "minor": None,
                "major_pentatonic": None,
                "minor_pentatonic": None,
                "blues": None,
            },
        }
    ]


class StorageManager:
    def __init__(self):
        self.config_path = path.join(environ["HOME"], ".config/guitartrainer")
        self.settings_file = path.join(self.config_path, "settings.json")
        self._ensure_path()

    def _ensure_path(self):
        if not path.exists(self.config_path):
            mkdir(self.config_path)

    def _load_config(self) -> Config:
        config = deepcopy(DEFAULT_CONFIG)
        if path.exists(self.settings_file):
            with open(self.settings_file, "r") as f:
                config.update(json.load(f))

        return config

    def _save_config(self, config: Config):
        self._ensure_path()
        with open(self.settings_file, "w") as f:
            json.dump(config, f)

    def _instrument_file(self, instrument: Instrument) -> str:
        return path.join(
            self.config_path,
            f"{instrument.value.name.lower()}.json",
        )

    def _load_instrument(self, instrument: Instrument) -> InstrumentData:
        instrument_file = self._instrument_file(instrument)

        instrument_data = gen_default_instrument(instrument)

        if path.exists(instrument_file):
            with open(instrument_file, "r") as f:
                data = json.load(f)
                if isinstance(data, list) and len(data) > 0:
                    instrument_data = data

        return instrument_data

    def _save_instrument(
        self,
        instrument: Instrument,
        progress: list[ProgressData],
    ):
        self._ensure_path()
        with open(self._instrument_file(instrument), "w") as f:
            json.dump(progress, f)

    def get_instrument_progress(
        self,
        instrument: Instrument,
    ) -> list[Progress]:
        return list(
            map(
                lambda data: Progress(
                    data["string_progress"],
                    data["highest_note"],
                    data["scales"],
                ),
                self._load_instrument(instrument),
            )
        )

    def set_instrument_progress(
        self,
        instrument: Instrument,
        progress: list[Progress],
    ):
        self._save_instrument(
            instrument,
            list(
                map(
                    lambda p: {
                        "string_progress": p.string_progress,
                        "highest_note": p.highest_note,
                        "scales": p.scales,
                    },
                    progress,
                )
            ),
        )

    @property
    def input_device(self) -> str | None:
        config = self._load_config()
        device = config.get("input_device", None)
        if isinstance(device, str):
            return device

        return None

    @input_device.setter
    def input_device(self, device: str | None):
        config = self._load_config()
        config["input_device"] = device
        self._save_config(config)
