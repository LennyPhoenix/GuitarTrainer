import json
from os import environ, path, mkdir
from typing import TypedDict
from copy import deepcopy


class Config(TypedDict):
    input_device: str | None


DEFAULT_CONFIG: Config = {"input_device": None}


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
