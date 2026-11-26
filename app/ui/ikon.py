import math
import tkinter as tk

from enum import StrEnum, auto

from app.common.rgbdata import RGBData
from app.ui.common import Px, C1, C2, DIM, KART, BG

_WHITE = RGBData(r=255, g=255, b=255)
_STROKE = Px(2)
_DEFAULT_SIZE = Px(22)

# Onceden hesaplanmis sabit vektor geometrileri (her cizimde sin/cos ve liste uretmemek icin)
_LIGHTNING_PTS: tuple[tuple[float, float], ...] = (
    (0.2, -1.0), (-0.6, 0.2), (-0.05, 0.2),
    (-0.2, 1.0), (0.6, -0.25), (0.05, -0.25),
)
_THICKNESS_BARS: tuple[tuple[float, float], ...] = (
    (-0.7, 0.2), (0.0, 0.38), (0.75, 0.62),
)
_SUN_RAYS: tuple[tuple[float, float], ...] = tuple(
    (math.cos(math.pi / 4 * i), math.sin(math.pi / 4 * i))
    for i in range(8)
)
_PALETTE_DOTS: tuple[tuple[float, float], ...] = tuple(
    (math.cos(a), math.sin(a))
    for a in (-math.pi / 2, math.pi / 6, 5 * math.pi / 6)
)
_WAVE_SAMPLES = 24
_WAVE_CURVE: tuple[tuple[float, float], ...] = tuple(
    (-1.0 + 2.0 * (i / _WAVE_SAMPLES), -0.55 * math.sin(3.0 * math.pi * (i / _WAVE_SAMPLES)))
    for i in range(_WAVE_SAMPLES + 1)
)

class IkonEnum(StrEnum):
    DALGA = auto()
    HIZ = auto()
    KALINLIK = auto()
    PARLAKLIK = auto()
    AY = auto()
    RENK = auto()
    KLAVYE = auto()
    OYNAT = auto()
    DURDUR = auto()

_DEFAULT_COLORS: dict[IkonEnum, RGBData] = {
    IkonEnum.DALGA: C1,
    IkonEnum.HIZ: C1,
    IkonEnum.KALINLIK: C1,
    IkonEnum.PARLAKLIK: C1,
    IkonEnum.RENK: C1,
    IkonEnum.AY: C2,
    IkonEnum.KLAVYE: DIM,
    IkonEnum.OYNAT: _WHITE,
    IkonEnum.DURDUR: _WHITE,
}

_DEFAULT_BGS: dict[IkonEnum, RGBData] = {
    IkonEnum.KLAVYE: BG,
}

class Ikon(tk.Canvas):
    def __init__(self, 
        ebeveyn, 
        ikon:IkonEnum, 
        renk:RGBData | None = None, 
        bg:RGBData | None = None, 
        boyut:Px = _DEFAULT_SIZE
    ) -> None:
        b = boyut.to_int()
        bg_color = bg if bg is not None else _DEFAULT_BGS.get(ikon, KART)
        super().__init__(
            ebeveyn, 
            width=b, height=b, 
            bg=bg_color.to_hex(), 
            highlightthickness=0, bd=0
        )
        Ikon.ciz(ikon, self, b/2, b/2, b*.38, renk, bg_color)

    @staticmethod
    def ciz(ikon:IkonEnum, 
            c:tk.Canvas, 
            cx:float, 
            cy:float, 
            s:float, 
            renk:RGBData | None = None, 
            bg:RGBData | None = None
    ) -> None:
        fg = renk if renk is not None else _DEFAULT_COLORS.get(ikon, C1)
        bg_color = bg if bg is not None else _DEFAULT_BGS.get(ikon, KART)

        match ikon:
            case IkonEnum.DALGA     : return Ikon.dalga(c, cx, cy, s, fg)
            case IkonEnum.HIZ       : return Ikon.hiz(c, cx, cy, s, fg)
            case IkonEnum.KALINLIK  : return Ikon.kalinlik(c, cx, cy, s, fg)
            case IkonEnum.PARLAKLIK : return Ikon.parlaklik(c, cx, cy, s, fg)
            case IkonEnum.AY        : return Ikon.ay(c, cx, cy, s, fg, bg_color)
            case IkonEnum.RENK      : return Ikon.renk(c, cx, cy, s, fg)
            case IkonEnum.KLAVYE    : return Ikon.klavye(c, cx, cy, s, fg)
            case IkonEnum.OYNAT     : return Ikon.oynat(c, cx, cy, s, fg)
            case IkonEnum.DURDUR    : return Ikon.durdur(c, cx, cy, s, fg)

    @staticmethod
    def _stroke() -> int:
        return max(1, _STROKE.to_int())

    @staticmethod
    def dalga(c: tk.Canvas, cx: float, cy: float, s: float, renk: RGBData) -> None:
        pts: list[float] = []
        for dx, dy in _WAVE_CURVE:
            pts.extend((cx + dx * s, cy + dy * s))
        c.create_line(*pts, smooth=True, width=Ikon._stroke(), fill=renk.to_hex(), capstyle="round")

    @staticmethod
    def hiz(c: tk.Canvas, cx: float, cy: float, s: float, renk: RGBData) -> None:
        scale = s * 0.95
        pts: list[float] = []
        for dx, dy in _LIGHTNING_PTS:
            pts.extend((cx + dx * scale, cy + dy * scale))
        c.create_polygon(*pts, fill=renk.to_hex(), outline="")

    @staticmethod
    def kalinlik(c: tk.Canvas, cx: float, cy: float, s: float, renk: RGBData) -> None:
        fill = renk.to_hex()
        for oy, hh in _THICKNESS_BARS:
            y = cy + oy * s
            half_h = hh * s / 2
            c.create_rectangle(cx - s, y - half_h, cx + s, y + half_h, fill=fill, outline="")

    @staticmethod
    def parlaklik(c: tk.Canvas, cx: float, cy: float, s: float, renk: RGBData) -> None:
        fill = renk.to_hex()
        kal = Ikon._stroke()
        r = s * 0.42
        c.create_oval(cx - r, cy - r, cx + r, cy + r, fill=fill, outline="")
        r_in = s * 0.68
        for cos_a, sin_a in _SUN_RAYS:
            c.create_line(
                cx + cos_a * r_in, cy + sin_a * r_in,
                cx + cos_a * s, cy + sin_a * s,
                width=kal, fill=fill, capstyle="round",
            )

    @staticmethod
    def ay(c: tk.Canvas, cx: float, cy: float, s: float, renk: RGBData, bg: RGBData) -> None:
        r = s * 0.85
        c.create_oval(cx - r, cy - r, cx + r, cy + r, fill=renk.to_hex(), outline="")
        r2 = s * 0.72
        ox, oy = cx + s * 0.5, cy - s * 0.3
        c.create_oval(ox - r2, oy - r2, ox + r2, oy + r2, fill=bg.to_hex(), outline="")

    @staticmethod
    def renk(c: tk.Canvas, cx: float, cy: float, s: float, renk: RGBData) -> None:
        fill = renk.to_hex()
        r = s * 0.95
        c.create_oval(cx - r, cy - r, cx + r, cy + r, outline=fill, width=Ikon._stroke())
        dot_dist = s * 0.5
        dot_r = s * 0.17
        for cos_a, sin_a in _PALETTE_DOTS:
            dx, dy = cx + cos_a * dot_dist, cy + sin_a * dot_dist
            c.create_oval(dx - dot_r, dy - dot_r, dx + dot_r, dy + dot_r, fill=fill, outline="")

    @staticmethod
    def klavye(c: tk.Canvas, cx: float, cy: float, s: float, renk: RGBData) -> None:
        fill = renk.to_hex()
        c.create_rectangle(
            cx - s, cy - s * 0.6, cx + s, cy + s * 0.6,
            outline=fill, width=Ikon._stroke(),
        )
        q = s * 0.12
        for row in (-0.25, 0.25):
            ky = cy + row * s
            for col in (-0.55, 0.0, 0.55):
                kx = cx + col * s
                c.create_rectangle(kx - q, ky - q, kx + q, ky + q, fill=fill, outline="")

    @staticmethod
    def oynat(c: tk.Canvas, cx: float, cy: float, s: float, renk: RGBData) -> None:
        c.create_polygon(
            cx - s * 0.55, cy - s * 0.8,
            cx + s * 0.8, cy,
            cx - s * 0.55, cy + s * 0.8,
            fill=renk.to_hex(), outline="",
        )

    @staticmethod
    def durdur(c: tk.Canvas, cx: float, cy: float, s: float, renk: RGBData) -> None:
        q = s * 0.65
        c.create_rectangle(cx - q, cy - q, cx + q, cy + q, fill=renk.to_hex(), outline="")
