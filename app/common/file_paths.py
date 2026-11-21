from pathlib import Path
from functools import lru_cache


@lru_cache(maxsize=1)
def get_root_dir() -> Path:
    return Path(__file__).parent.parent.parent

APP_DIR         = get_root_dir() / "app";       APP_DIR.mkdir(exist_ok=True, parents=True)
CONFIG_DIR      = get_root_dir() / "config";    CONFIG_DIR.mkdir(exist_ok=True, parents=True)
LOGS_DIR        = get_root_dir() / "logs";      LOGS_DIR.mkdir(exist_ok=True, parents=True)
LOCALE_DIR      = get_root_dir() / "locales"

