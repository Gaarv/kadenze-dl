from dataclasses import dataclass
from enum import Enum, unique
from pathlib import Path
from typing import Dict, List, Optional

from yaml import Loader, load


@unique
class Resolution(Enum):
    _360 = "360"
    _720 = "720"


@dataclass
class Settings:
    login: str
    password: str
    download_path: Path
    courses: List[str]
    resolution: Resolution
    proxy: Optional[str] = None

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "instance"):
            cls.instance = super(Settings, cls).__new__(cls)
        return cls.instance


def build_settings(
    courses: List[str],
    resolution: str,
    config_file: Optional[Path] = None,
    login: Optional[str] = None,
    password: Optional[str] = None,
    download_path: Optional[Path] = None,
    proxy: Optional[str] = None,
) -> Settings:
    try:
        if config_file and config_file.exists():
            # use input config file and merge with defaults
            with open(config_file, "r") as f:
                d: Dict = load(f, Loader=Loader)
                _login: str = d["kadenze"]["login"]
                _password: str = d["kadenze"]["password"]
                _download_path = Path(d["download"]["download_path"])
                _courses = d["download"]["courses"]
                _resolution = d["download"]["resolution"]
                _proxy = str(d["download"]["proxy"]) or None
                return Settings(_login, _password, _download_path, _courses, Resolution[f"_{_resolution}"], _proxy)
        else:
            # use provided arguments from CLI
            if all([login, password, download_path]):
                config = {}
                config["login"] = login
                config["password"] = password
                config["download_path"] = download_path
                config["resolution"] = Resolution[f"_{resolution}"]
                config["courses"] = courses
                config["proxy"] = proxy
                return Settings(**config)

            else:
                raise ValueError("No config file and or no mandatory arguments were provided. Check --help")

    except Exception as e:
        raise ValueError(f"Error while building configuration from file or provided arguments: {e}")
