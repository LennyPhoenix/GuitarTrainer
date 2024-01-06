import json
from os import environ, path, mkdir
from typing import TypedDict
from copy import deepcopy

from .instrument import Instrument


class Config(TypedDict):
    input_device: str | None


DEFAULT_CONFIG: Config = {"input_device": None}


class InstrumentProgress(TypedDict):
    string_progress: list[tuple[int, int]]
    highest_note: tuple[int, int]
    scales: dict[str, tuple[bool, bool]]
    # TODO: Store lessons


def gen_default(instrument: Instrument) -> InstrumentProgress:
    return {
        "string_progress": [(0, 0)] * len(instrument.value.strings),
        "highest_note": (0, 0),
        "scales": {},  # TODO
    }


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

    def _load_instrument(self, instrument: Instrument) -> InstrumentProgress:
        instrument_file = self._instrument_file(instrument)
        progress = gen_default(instrument)
        if path.exists(instrument_file):
            with open(instrument_file, "r") as f:
                progress.update(json.load(f))
        return progress

    def _save_instrument(
        self,
        instrument: Instrument,
        progress: InstrumentProgress,
    ):
        self._ensure_path()
        with open(self._instrument_file(instrument), "w") as f:
            json.dump(progress, f)

    def get_string_progress(
        self,
        instrument: Instrument,
        string: int,
    ) -> tuple[int, int]:
        return self._load_instrument(instrument)["string_progress"][string]

    def set_string_progress(
        self,
        instrument: Instrument,
        string: int,
        progress: tuple[int, int],
    ):
        instrument_progress = self._load_instrument(instrument)
        instrument_progress["string_progress"][string] = progress
        self._save_instrument(instrument, instrument_progress)

    def get_highest_note(
        self,
        instrument: Instrument,
    ) -> tuple[int, int]:
        return self._load_instrument(instrument)["highest_note"]

    def set_highest_note(
        self,
        instrument: Instrument,
        note: tuple[int, int],
    ):
        instrument_progress = self._load_instrument(instrument)
        instrument_progress["highest_note"] = note
        self._save_instrument(instrument, instrument_progress)

    def get_scale(
        self,
        instrument: Instrument,
        scale: str,
    ) -> tuple[bool, bool]:
        return self._load_instrument(instrument)["scales"].get(
            scale,
            (False, False),
        )

    def set_scale(
        self,
        instrument: Instrument,
        scale: str,
        value: tuple[bool, bool],
    ):
        instrument_progress = self._load_instrument(instrument)
        instrument_progress["scales"][scale] = value
        self._save_instrument(instrument, instrument_progress)

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
