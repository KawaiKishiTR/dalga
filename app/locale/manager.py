from functools import lru_cache
from typing import ClassVar
import yaml

from app.locale.models import LocaleSchema
from app.common.file_paths import LOCALE_DIR

class LocaleManager:
    def __new__(cls):
        return cls.get_texts()

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
        if not LOCALE_DIR.exists():
            return [cls.default_lang]
        langs = sorted(p.stem for p in LOCALE_DIR.glob("*.yml"))
        return langs or [cls.default_lang]

    @classmethod
    @lru_cache(maxsize=1)
    def get_texts(cls) -> LocaleSchema:
        file_path = LOCALE_DIR / f"{cls._current_lang}.yml"
        if not file_path.exists():
            file_path = LOCALE_DIR / f"{cls.default_lang}.yml"

        data = {}
        if file_path.exists():
            with file_path.open("r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}

        return LocaleSchema.model_validate(data)