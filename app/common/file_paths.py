import sys
from pathlib import Path

if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys.executable).parent          # .exe'nin bulunduğu klasör (config için)
    RESOURCE_DIR = Path(sys._MEIPASS)               # gömülü dosyalar (locale vb. için)
else:
    BASE_DIR = Path(__file__).resolve().parents[2]
    RESOURCE_DIR = BASE_DIR

CONFIG_DIR      = BASE_DIR      / "config";    CONFIG_DIR.mkdir(exist_ok=True, parents=True)
LOGS_DIR        = BASE_DIR      / "logs";      LOGS_DIR.mkdir(exist_ok=True, parents=True)
LOCALE_DIR      = RESOURCE_DIR  / "locales"

