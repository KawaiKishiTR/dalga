import tkinter as tk
from typing import Callable

from app.common.rgbdata import RGBData
from app.ui.base.mixins import ClickableMixin, DrawOnInitMixin
from app.ui.common import (
    Px, C1, C2, DEVRE, TRACK
)

_HEIGHT = Px(30)
_PAD_X = Px(12)
_TRACK_THICKNESS = Px(6)
_GRADIENT_STEP = Px(5)
_KNOB_RADIUS = Px(9)
_GLOW_SPREAD = Px(4)

_KNOB_ACTIVE = "#ffffff"
_KNOB_DISABLED = "#9a9ab0"

class Kaydirici(DrawOnInitMixin, ClickableMixin, tk.Canvas):
    """Gradyan dolgulu, parlayan topuzlu kaydirici."""

    def __init__(self, 
            ebeveyn: tk.Misc, 
            alt: float, 
            ust: float, 
            adim: float, 
            deger: float, 
            komut: Callable[[float], None] | None, 
            bg:RGBData,
            yukseklik: Px = _HEIGHT
    ) -> None:
        self.alt = float(alt)
        self.ust = float(ust) 
        self.adim = float(adim)
        self._deger = self._clamp(float(deger))
        self.komut = komut
        self.bgc:RGBData = bg
        self._aktif = True
        super().__init__(
            ebeveyn, 
            height=yukseklik.to_int(), 
            bg=bg.to_hex(), 
            highlightthickness=0, 
            bd=0, 
            cursor="hand2"
        )
        self.bind("<B1-Motion>", self._handle_L_click)

    @property
    def aktif(self) -> bool:
        return self._deger

    @aktif.setter
    def aktif(self, value:bool) -> None:
        value = bool(value)
        if self._aktif != value:
            self._aktif = value
            self.configure(cursor="hand2" if value else "")
            self._handle_draw()

    @property
    def deger(self) -> float:
        return self._deger

    @deger.setter
    def deger(self, value:float) -> None:
        clamped = self._clamp(float(value))
        if self._deger != value:
            self._deger = value
            self._handle_draw()

    def _clamp(self, value: float) -> float:
        return max(self.alt, min(self.ust, value))

    def _ratio(self) -> float:
        span = self.ust - self.alt
        if span <= 0:
            return 0.0
        return max(0.0, min(1.0, (self._deger - self.alt) / span))

    def _draw_track(self, x0: float, x1: float, xv: float, y: float, c1: RGBData, c2: RGBData) -> None:
        kal = _TRACK_THICKNESS.to_int()
        self.create_line(x0, y, x1, y, width=kal, capstyle="round", fill=TRACK.to_hex())

        if xv <= x0 + 1:
            return

        if c1 == c2:
            self.create_line(x0, y, xv, y, width=kal, capstyle="round", fill=c1.to_hex())
            return

        step = max(1, _GRADIENT_STEP.to_int())
        n = max(2, int((xv - x0) / step))
        span = xv - x0
        for i in range(n):
            a = x0 + span * i / n
            b = x0 + span * (i + 1) / n
            color = c1.lerp(c2, (i + 0.5) / n).to_hex()
            self.create_line(a, y, b + 1, y, width=kal, fill=color)

        half_k = kal / 2
        self.create_oval(x0 - half_k, y - half_k, x0 + half_k, y + half_k, fill=c1.to_hex(), outline="")

    def _draw_knob(self, xv: float, y: float, knob_color: RGBData) -> None:
        r = _KNOB_RADIUS.to_int()
        glow_r = r + _GLOW_SPREAD.to_int()
        self.create_oval(
            xv - glow_r, y - glow_r, xv + glow_r, y + glow_r,
            fill=self.bgc.lerp(knob_color, 0.22).to_hex(), outline="",
        )
        self.create_oval(
            xv - r, y - r, xv + r, y + r,
            fill=_KNOB_ACTIVE if self._aktif else _KNOB_DISABLED,
            outline=knob_color.to_hex(),
            width=2,
        )

    def _handle_draw(self) -> None:
        self.delete("all")
        w = self.winfo_width()
        h = self.winfo_height()
        if w <= 2 or h <= 2:
            return

        pad = _PAD_X.to_int()
        y = h / 2
        x0, x1 = float(pad), float(w - pad)
        ratio = self._ratio()
        xv = x0 + (x1 - x0) * ratio
        c1, c2 = (C1, C2) if self._aktif else (DEVRE, DEVRE)

        self._draw_track(x0, x1, xv, y, c1, c2)
        self._draw_knob(xv, y, c1.lerp(c2, ratio))

    def _handle_L_click(self, event: tk.Event):
        if not self._aktif:
            return
        w = self.winfo_width()
        pad = _PAD_X.to_int()
        ratio = (event.x - pad) / float(max(1, w - 2 * pad))
        ratio = max(0.0, min(1.0, ratio))
        raw = self.alt + ratio * (self.ust - self.alt)
        snapped = self.alt + round((raw - self.alt) / self.adim) * self.adim
        val = round(self._clamp(snapped), 2)
        if val != self._deger:
            self._deger = val
            self._handle_draw()
            if self.komut is not None:
                self.komut(val)
