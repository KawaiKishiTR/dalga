import tkinter as tk
from typing import Callable

from app.common.rgbdata import RGBData
from app.ui.base.mixins import ClickableMixin
from app.ui.common import Px, DEVRE

_DEFAULT_SIZE = Px(36)
_MARGIN = Px(4)
_BORDER_COLOR = "#3a3a58"
_RAINBOW_SLICES = 12
_SLICE_ANGLE = 360.0 / _RAINBOW_SLICES
_RAINBOW_COLORS: tuple[str, ...] = tuple(
    RGBData.from_hsv(i / _RAINBOW_SLICES, 1.0, 1.0).to_hex()
    for i in range(_RAINBOW_SLICES)
)

class Ornek(ClickableMixin, tk.Canvas):
    """Renk ornegi (yuvarlak). Gokkusagi modunda gokkusagi diski gosterir."""

    def __init__(self, 
            ebeveyn: tk.Misc, 
            renk:RGBData, 
            komut: Callable[[], None] | None, 
            bg:RGBData, 
            boyut:Px = _DEFAULT_SIZE
    ) -> None:
        self._size = boyut.to_int()
        self._renk = renk
        self.komut = komut
        self._gokkusagi = False
        self._aktif = True

        super().__init__(ebeveyn, 
            width=self._size, height=self._size, 
            bg=bg.to_hex(),
            highlightthickness=0, bd=0, 
            cursor="hand2"
        )
        self.draw()

    @property
    def renk(self) -> RGBData:
        return self._renk

    @renk.setter
    def renk(self, value: RGBData) -> None:
        if self._renk != value:
            self._renk = value
            self.draw()

    @property
    def gokkusagi(self) -> bool:
        return self._gokkusagi

    @gokkusagi.setter
    def gokkusagi(self, value: bool) -> None:
        value = bool(value)
        if self._gokkusagi != value:
            self._gokkusagi = value
            self._sync_cursor()
            self.draw()

    @property
    def aktif(self) -> bool:
        return self._aktif

    @aktif.setter
    def aktif(self, value: bool) -> None:
        value = bool(value)
        if self._aktif != value:
            self._aktif = value
            self._sync_cursor()
            self.draw()

    def _is_clickable(self) -> bool:
        return self._aktif and not self._gokkusagi

    def _sync_cursor(self) -> None:
        self.configure(cursor="hand2" if self._is_clickable() else "")

    def draw(self) -> None:
        self.delete("all")
        b = self._size
        m = _MARGIN.to_int()

        if self._gokkusagi:
            for i, color in enumerate(_RAINBOW_COLORS):
                self.create_arc(
                    m, m, b - m, b - m,
                    start=i * _SLICE_ANGLE,
                    extent=_SLICE_ANGLE,
                    fill=color,
                    outline="",
                )
        else:
            fill = self._renk.to_hex() if self._aktif else DEVRE.to_hex()
            self.create_oval(m, m, b - m, b - m, fill=fill, outline="")

        self.create_oval(1, 1, b - 1, b - 1, outline=_BORDER_COLOR, width=2)

    def _handle_L_click(self, event: tk.Event) -> None:
        if self._is_clickable() and self.komut is not None:
            self.komut()