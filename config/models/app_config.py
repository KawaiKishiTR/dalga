from functools import lru_cache
from pathlib import Path
from typing import Annotated, Any, ClassVar, Literal
import yaml
from pydantic import BaseModel, Field, ValidationError, ValidationInfo, field_validator

HexColor = Annotated[str, Field(pattern=r"^#[0-9a-fA-F]{6}$")]


class AppConfig(BaseModel):
    hiz: float = Field(default=8.0, ge=2.0, le=20.0)
    kalinlik: float = Field(default=1.6, ge=0.8, le=4.0)
    parlaklik: int = Field(default=100, ge=5, le=100)
    mod: Literal["gokkusagi", "sabit"] = "gokkusagi"
    renk: HexColor = "#00d4ff"
    bekleme_acik: bool = False
    bekleme_renk: HexColor = "#3b1fa3"
    bekleme_parlaklik: int = Field(default=35, ge=1, le=100)
    omur: float = Field(default=0.55, gt=0)
    fps: int = Field(default=25, gt=0)
    max_dalga: int = Field(default=8, ge=1)

    # sınıf değişkenleri
    config_file: ClassVar[Path] = Path("./config/config.yml").resolve()

    # Sıkıştırılacak alanlar: (alt_sinir, ust_sinir, tam_sayi_mi)
    _LIMITS: ClassVar[dict[str, tuple[float, float, bool]]] = {
        "hiz": (2.0, 20.0, False),
        "kalinlik": (0.8, 4.0, False),
        "parlaklik": (5, 100, True),
        "bekleme_parlaklik": (1, 100, True),
    }

    @field_validator("hiz", "kalinlik", "parlaklik", "bekleme_parlaklik", mode="before")
    @classmethod
    def _clamp_numeric(cls, v: Any, info: ValidationInfo) -> Any:
        alt, ust, is_int = cls._LIMITS[info.field_name]
        try:
            num = float(v)
        except (TypeError, ValueError):
            return cls.model_fields[info.field_name].default
        num = max(alt, min(ust, num))
        return int(round(num)) if is_int else round(num, 2)

    @field_validator("renk", "bekleme_renk", "mod", "bekleme_acik", "omur", "fps", "max_dalga", mode="wrap")
    @classmethod
    def _fallback_default(cls, v: Any, handler: Any, info: ValidationInfo) -> Any:
        try:
            return handler(v)
        except ValidationError:
            return cls.model_fields[info.field_name].default

    @classmethod
    @lru_cache(maxsize=1)
    def get_config(cls) -> AppConfig:
        user_data = {}
        if cls.config_file.exists():
            with cls.config_file.open("r", encoding="utf-8") as f:
                user_data = yaml.safe_load(f) or {}
        return cls.model_validate(user_data)

    def set_config(self) -> None:
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        with self.config_file.open("w", encoding="utf-8") as f:
            yaml.safe_dump(self.model_dump(), f, sort_keys=False, allow_unicode=True)
        type(self).get_config.cache_clear()
