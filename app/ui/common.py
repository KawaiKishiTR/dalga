import tkinter as tk

from dataclasses import dataclass
from typing import ClassVar

from app.common.rgbdata import RGBData

# ----------------------------- TASARIM -----------------------------
BG = RGBData.from_hex("#0a0a12")
KART = RGBData.from_hex("#13131f")
KENAR = RGBData.from_hex("#232338")
TRACK = RGBData.from_hex("#25253a")
DEVRE = RGBData.from_hex("#3a3a52")
FG = RGBData.from_hex("#eceaf8")
DIM = RGBData.from_hex("#7c7a99")
C1 = RGBData.from_hex("#00d4ff")   # camgobegi
C2 = RGBData.from_hex("#8b5cff")   # mor
DUR1 = RGBData.from_hex("#ff6b8a")
DUR2 = RGBData.from_hex("#ff2d6f")
YESIL = RGBData.from_hex("#3ddc97")
HATA = RGBData.from_hex("#ff5d73")

FONT = "Segoe UI"

@dataclass(frozen=True, slots=True)
class Px:
    """Mantıksal (ölçeklenmemiş) piksel değeri. Çizim/Tkinter sınırında fiziksel piksele çevrilir."""

    value: float

    _scale: ClassVar[float] = 1.0

    @classmethod
    def set_scale(cls, scale: float) -> None:
        if scale <= 0:
            raise ValueError("Scale must be positive")
        cls._scale = float(scale)

    @classmethod
    def get_scale(cls) -> float:
        return cls._scale

    # --- Fiziksel piksele dönüşüm (RGBData.to_hex() ile aynı yaklaşım) ---
    def to_int(self) -> int:
        return int(round(self.value * self._scale))

    def to_float(self) -> float:
        return self.value * self._scale

    # Tkinter doğrudan str() / int() çağırdığı için padx=Px(16) şeklinde de çalışır
    def __int__(self) -> int:
        return self.to_int()

    def __float__(self) -> float:
        return self.to_float()

    def __str__(self) -> str:
        return str(self.to_int())

    # --- Mantıksal aritmetik (yuvarlama hatası birikmez) ---
    def __add__(self, other: "Px") -> "Px":
        if not isinstance(other, Px):
            return NotImplemented
        return Px(self.value + other.value)

    def __sub__(self, other: "Px") -> "Px":
        if not isinstance(other, Px):
            return NotImplemented
        return Px(self.value - other.value)

    def __mul__(self, factor: int | float) -> "Px":
        if not isinstance(factor, (int, float)):
            return NotImplemented
        return Px(self.value * factor)

    def __rmul__(self, factor: int | float) -> "Px":
        return self.__mul__(factor)

    def __truediv__(self, factor: int | float) -> "Px":
        if not isinstance(factor, (int, float)):
            return NotImplemented
        return Px(self.value / factor)

    def __neg__(self) -> "Px":
        return Px(-self.value)