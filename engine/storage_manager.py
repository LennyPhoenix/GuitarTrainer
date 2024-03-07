import json
from os import environ, path, mkdir
from typing import TypedDict
from copy import deepcopy

from .instrument import Instrument
from .progress import Progress
from .note import Note


class Config(TypedDict):
    """Type definition for the user's stored settings."""

    input_device: str | None
    tuner_accidentals: str
    default_instrument: str


DEFAULT_CONFIG: Config = {
    "input_device": None,
    "tuner_accidentals": Note.Mode.SHARPS.name,
    "default_instrument": Instrument.GUITAR.name,
}


class ProgressData(TypedDict):
    """Type definition for the user's progress at a given point."""

    string_progress: list[tuple[int | None, int | None]]
    highest_note: tuple[int | None, int | None]
    scales: dict[str, tuple[bool, bool]]


InstrumentData = list[ProgressData]


def gen_default_instrument(instrument: Instrument) -> InstrumentData:
    return [
        {
            "string_progress": [(None, None)] * len(instrument.value.strings),
            "highest_note": (None, None),
            "scales": {},
        }
    ]


class StorageManager:
    """Provides a seamless translation layer between the engine and the
    filesystem, allowing all data to be saved to disk.

    Data is provided with properties and functions, meaning that the storage
    manager is entirely stateless.
    This should mean that data never falls out of sync, as there is no data
    stored in the engine that isn't fetched on demand.
    """

    def __init__(self):
        # Sets the path to the default config directory
        self.config_path = path.join(environ["HOME"], ".config/guitartrainer")
        self.settings_file = path.join(self.config_path, "settings.json")
        self._ensure_path()

    def _ensure_path(self):
        """Ensures that the configuration directory actually exists."""
        if not path.exists(self.config_path):
            mkdir(self.config_path)

    def _load_config(self) -> Config:
        """Reads the settings file from disk and returns as a Config
        dictionary."""
        config = deepcopy(DEFAULT_CONFIG)
        if path.exists(self.settings_file):
            with open(self.settings_file, "r") as f:
                config.update(json.load(f))

        return config

    def _save_config(self, config: Config):
        """Saves a configuration to disk."""
        # Make sure the config path exists before writing to it
        self._ensure_path()
        with open(self.settings_file, "w") as f:
            json.dump(config, f)

    def _instrument_file(self, instrument: Instrument) -> str:
        """Returns the file path for a specific instrument."""
        return path.join(
            self.config_path,
            f"{instrument.value.name.lower()}.json",
        )

    def _load_instrument(self, instrument: Instrument) -> InstrumentData:
        """Returns the instrument data for a specific instrument."""
        instrument_file = self._instrument_file(instrument)

        # Get default data
        instrument_data = gen_default_instrument(instrument)

        # If saved config exists, return this instead
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
        """Saves instrument data to disk."""
        self._ensure_path()
        with open(self._instrument_file(instrument), "w") as f:
            json.dump(progress, f)

    def get_instrument_progress(
        self,
        instrument: Instrument,
    ) -> list[Progress]:
        """Fetches instrument data from disk and maps to a list of `Progress`
        objects."""
        return list(
            map(
                # Convert each dictionary to a `Progress` object
                lambda data: Progress(
                    data["string_progress"],
                    data["highest_note"],
                    {
                        # Add missing scales into progress snapshot, defaulting
                        # to unlearnt
                        scale.name: (
                            data["scales"][scale.name]
                            if scale.name in data["scales"].keys()
                            else (False, False)
                        )
                        for scale in instrument.value.scales
                    },
                ),
                self._load_instrument(instrument),
            )
        )

    def set_instrument_progress(
        self,
        instrument: Instrument,
        progress: list[Progress],
    ):
        """Saves an instrument's progress list to disk."""
        self._save_instrument(
            instrument,
            list(
                map(
                    # Convert each object to a dictionary to be saved to JSON
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
        """The user's input device, or None if it is not assigned."""
        config = self._load_config()
        device = config.get("input_device", None)
        if isinstance(device, str):
            return device

        return None

    @input_device.setter
    def input_device(self, device: str | None):
        # Fetch the previous config,
        config = self._load_config()
        # overwrite the input device,
        config["input_device"] = device
        # then save.
        self._save_config(config)

    @property
    def tuner_accidentals(self) -> Note.Mode:
        """The user's accidental preference on the tuner."""
        config = self._load_config()
        return Note.Mode[config.get("tuner_accidentals", Note.Mode.SHARPS.name)]

    @tuner_accidentals.setter
    def tuner_accidentals(self, tuner_accidentals: Note.Mode):
        config = self._load_config()
        config["tuner_accidentals"] = tuner_accidentals.name
        self._save_config(config)

    @property
    def default_instrument(self) -> Instrument:
        """The default instrument when opening any menu."""
        config = self._load_config()
        return Instrument[config.get("default_instrument", Instrument.GUITAR.name)]

    @default_instrument.setter
    def default_instrument(self, default_instrument: Instrument):
        config = self._load_config()
        config["default_instrument"] = default_instrument.name
        self._save_config(config)
