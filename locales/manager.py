from functools import lru_cache
from pathlib import Path
from typing import ClassVar
import yaml
from pydantic import BaseModel


class HeaderLocale(BaseModel):
    app_name: str = "DALGA"
    subtitle: str = "Her tuşa bastığında ışık dalgası yayılır"


class StatusLocale(BaseModel):
    stopped: str = "Durdu"
    running: str = "Çalışıyor"
    keyboard_not_found: str = "Klavye bulunamadı. GG / OpenRGB kapalı mı?"
    connection_lost: str = "Bağlantı koptu, yeniden deneniyor..."


class EffectLocale(BaseModel):
    card_title: str = "EFEKT"
    speed: str = "Hız"
    thickness: str = "Kalınlık"
    brightness: str = "Parlaklık"


class ColorLocale(BaseModel):
    card_title: str = "RENK"
    wave_color: str = "Dalga rengi"
    rainbow: str = "Gökkuşağı"
    solid: str = "Sabit renk"
    pick_color: str = "Renk seç"
    dialog_title: str = "Dalga rengi"


class StandbyLocale(BaseModel):
    card_title: str = "BEKLEME IŞIĞI"
    toggle_label: str = "Bekleme ışığı"
    pick_color: str = "Renk seç"
    dialog_title: str = "Bekleme ışığı rengi"
    brightness: str = "Parlaklık"


class ActionLocale(BaseModel):
    start: str = "BAŞLAT"
    stop: str = "DURDUR"


class LocaleSchema(BaseModel):
    header: HeaderLocale = HeaderLocale()
    status: StatusLocale = StatusLocale()
    effect: EffectLocale = EffectLocale()
    color: ColorLocale = ColorLocale()
    standby: StandbyLocale = StandbyLocale()
    actions: ActionLocale = ActionLocale()


class LocaleManager:
    def __new__(cls):
        return cls.get_texts()

    locales_dir: ClassVar[Path] = Path("./locales").resolve()
    default_lang: ClassVar[str] = "tr"
    _current_lang: ClassVar[str] = "tr"

    @classmethod
    def set_language(cls, lang: str) -> LocaleSchema:
        cls._current_lang = lang.lower().strip()
        cls.get_texts.cache_clear()
        return cls.get_texts()

    @classmethod
    def get_language(cls) -> str:
        return cls._current_lang

    @classmethod
    def available_languages(cls) -> list[str]:
        if not cls.locales_dir.exists():
            return [cls.default_lang]
        langs = sorted(p.stem for p in cls.locales_dir.glob("*.yml"))
        return langs or [cls.default_lang]

    @classmethod
    @lru_cache(maxsize=1)
    def get_texts(cls) -> LocaleSchema:
        file_path = cls.locales_dir / f"{cls._current_lang}.yml"
        if not file_path.exists():
            file_path = cls.locales_dir / f"{cls.default_lang}.yml"

        data = {}
        if file_path.exists():
            with file_path.open("r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}

        return LocaleSchema.model_validate(data)