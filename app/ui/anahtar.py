import tkinter as tk
from typing import Callable

from app.common.rgbdata import RGBData
from app.ui.base.mixins import ClickableMixin
from app.ui.common import (
    Px, C1, C2, TRACK
)

_KNOB_ON = "#ffffff"
_KNOB_OFF = "#8a8aa6"
_KNOB_PAD = Px(3)
_GRADIENT_STEP = 2

class Anahtar(ClickableMixin, tk.Canvas):
    """Ac/kapa anahtari."""

    def __init__(
            self, 
            ebeveyn: tk.Misc, 
            deger: bool, 
            komut: Callable[[bool], None] | None, 
            bg:RGBData,
            genislik:Px = Px(48),
            yukseklik:Px = Px(26)
    ) -> None:
        self._genislik = genislik.to_int()
        self._yukseklik = yukseklik.to_int()
        self._deger = bool(deger)
        self.komut = komut
        super().__init__(ebeveyn, width=self._genislik, height=self._yukseklik, bg=bg.to_hex(),
                         highlightthickness=0, bd=0, cursor="hand2")
        self.draw()

    @property
    def deger(self) -> bool:
        return self._deger

    @deger.setter
    def deger(self, value:bool) -> None:
        value = bool(value)
        if self._deger != value:
            self._deger = value
            self.draw()

    def _draw_track(self) -> None:
        w, h = self._genislik, self._yukseklik
        x_start = h // 2
        x_end = w - x_start

        if not self._deger:
            track_hex = TRACK.to_hex()
            self.create_oval(0, 0, h, h, fill=track_hex, outline="")
            self.create_oval(w - h, 0, w, h, fill=track_hex, outline="")
            if x_end > x_start:
                self.create_rectangle(x_start, 0, x_end, h, fill=track_hex, outline="")
            return

        self.create_oval(0, 0, h, h, fill=C1.to_hex(), outline="")
        self.create_oval(w - h, 0, w, h, fill=C2.to_hex(), outline="")
        if x_end > x_start:
            span = float(x_end - x_start)
            for x in range(x_start, x_end, _GRADIENT_STEP):
                color = C1.lerp(C2, (x - x_start) / span).to_hex()
                self.create_line(x, 0, x, h, fill=color, width=_GRADIENT_STEP + 1)

    def _draw_knob(self) -> None:
        w, h = self._genislik, self._yukseklik
        cy = h / 2
        r = cy - _KNOB_PAD.to_int()
        kx = (w - cy) if self._deger else cy
        fill = _KNOB_ON if self._deger else _KNOB_OFF
        self.create_oval(kx - r, cy - r, kx + r, cy + r, fill=fill, outline="")

    def draw(self) -> None:
        self.delete("all")
        self._draw_track()
        self._draw_knob()

    def _handle_L_click(self, e):
        self.deger = not self.deger
        if self.komut is not None:
            self.komut(self._deger)
