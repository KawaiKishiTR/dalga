import re
from typing import Annotated, Any, ClassVar, Literal
from pydantic import (
    BaseModel,
    ConfigDict,
    PlainSerializer,
    BeforeValidator,
    ValidationError,
    ValidationInfo,
    Field,
    field_validator
)

from app.config.config_mixin import ConfigModelMixin
from app.common.rgbdata import RGBData

HEX_PATTERN = re.compile(r"^#[0-9a-fA-F]{6}$")

def _parse_hex_to_rgb(v: Any) -> Any:
    if isinstance(v, RGBData):
        return v
    if isinstance(v, str):
        if not HEX_PATTERN.match(v):
            raise ValueError(f"Geçersiz hex renk kodu: {v}")
        return RGBData.from_hex(v)
    return v

HexRGB = Annotated[
    RGBData,
    BeforeValidator(_parse_hex_to_rgb),
    PlainSerializer(lambda v: v.to_hex(), return_type=str)
]



class AppConfig(BaseModel, ConfigModelMixin):
    model_config = ConfigDict(validate_assignment=True)
    dil: str = Field(default="tr")
    hiz: float = Field(default=8.0, ge=2.0, le=20.0)
    kalinlik: float = Field(default=1.6, ge=0.8, le=4.0)
    parlaklik: int = Field(default=100, ge=5, le=100)
    mod: Literal["gokkusagi", "sabit"] = "gokkusagi"
    renk: HexRGB = Field(default_factory=lambda: RGBData.from_hex("#00d4ff"))
    bekleme_acik: bool = False
    bekleme_renk: HexRGB = Field(default_factory=lambda: RGBData.from_hex("#3b1fa3"))
    bekleme_parlaklik: int = Field(default=35, ge=1, le=100)
    omur: float = Field(default=0.55, gt=0)
    fps: int = Field(default=25, gt=0)
    max_dalga: int = Field(default=8, ge=1)

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
            field = cls.model_fields[info.field_name]
            return field.default_factory() if field.default_factory is not None else field.default