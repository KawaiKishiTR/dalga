import colorsys

from pydantic import BaseModel, Field, ValidationInfo, field_validator


def clamp(_min:float, _max:float, v:float):
    return min(_max, max(_min, v))

class RGBData(BaseModel):
    r:float = Field(ge=0, lt=256)
    g:float = Field(ge=0, lt=256)
    b:float = Field(ge=0, lt=256)

    @classmethod
    def from_hsv(cls, h, s, v):
        return cls.from_tuple(colorsys.hsv_to_rgb(h, s, v)) * 255

    @classmethod
    def from_hex(cls, hex:str):
        hex = hex.lstrip("#")
        return cls.from_tuple(tuple(int(hex[i:i + 2], 16) for i in (0, 2, 4)))

    def to_hex(self) -> str:
        return "#%02x%02x%02x" % self.to_tuple_round()

    @classmethod
    def from_tuple(cls, rgb:tuple):
        return cls(r=rgb[0], g=rgb[1], b=rgb[2])

    def to_tuple(self) -> tuple:
        return (self.r, self.g, self.b)

    def to_tuple_round(self) -> tuple:
        return tuple(round(i) for i in self.to_tuple())

    def lerp(self, other:"RGBData", t:float) -> "RGBData":
        t = clamp(0, 1, t)

        return RGBData(
            r=self.r + (other.r - self.r) * t,
            g=self.g + (other.g - self.g) * t,
            b=self.b + (other.b - self.b) * t,
        )

    @field_validator("r", "g", "b", mode="before")
    @classmethod
    def _clamp_numeric(cls, v:float, info:ValidationInfo) -> float:
        try:
            _ = float(v)
        except (TypeError, ValueError) as e:
            raise ValueError("RGB alanları mutlaka float olmalı") from e
        return clamp(0, 255, float(v))

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return RGBData(r=self.r * other,
                           g=self.g * other,
                           b=self.b * other)
        raise TypeError(f"{self.__class__} ve {type(other)} birbirleri ile çarpılamaz")

    def __eq__(self, other):
        if isinstance(other, RGBData):
            if (self.r == other.r and
                self.g == other.g and
                self.b == other.b):
                return True
            return False
        if isinstance(other, str):
            if self.to_hex() == other:
                return True
            return False
        if isinstance(other, tuple):
            if (self.to_tuple() == other or
                self.to_tuple_round() == other):
                return True
            return False 
        return NotImplemented

        