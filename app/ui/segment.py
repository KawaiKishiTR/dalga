import tkinter as tk
from collections.abc import Callable, Sequence
from typing import Generic, TypeVar

from app.common.rgbdata import RGBData
from app.ui.base.mixins import ClickableMixin, DrawOnInitMixin
from app.ui.common import (
    C1, C2, DIM, FONT, TRACK, Px
)

T = TypeVar("T")

_HEIGHT = Px(38)
_INNER_PAD = Px(3)
_TEXT_ACTIVE = "#ffffff"


class Segment(DrawOnInitMixin, ClickableMixin, tk.Canvas, Generic[T]):
    """Cok secenekli kapsul secici."""

    def __init__(
        self,
        ebeveyn: tk.Misc,
        secenekler: Sequence[tuple[str, T]],
        secili: T,
        komut: Callable[[T], None] | None,
        bg: RGBData,
        yukseklik: Px = _HEIGHT,
    ) -> None:
        self.secenekler: list[tuple[str, T]] = list(secenekler)
        self._secili: T = secili
        self.komut = komut

        super().__init__(
            ebeveyn,
            height=yukseklik.to_int(),
            bg=bg.to_hex(),
            highlightthickness=0,
            bd=0,
            cursor="hand2",
        )

    @property
    def secili(self) -> T:
        return self._secili

    @secili.setter
    def secili(self, value: T) -> None:
        if self._secili != value:
            self._secili = value
            self._handle_draw()

    def _draw_pill(self, x1: float, y1: float, x2: float, y2: float, fill: str) -> None:
        h = y2 - y1
        if h <= 0 or x2 <= x1:
            return
        r = min(h / 2, (x2 - x1) / 2)
        d = 2 * r
        self.create_oval(x1, y1, x1 + d, y2, fill=fill, outline="")
        self.create_oval(x2 - d, y1, x2, y2, fill=fill, outline="")
        if x2 - x1 > d:
            self.create_rectangle(x1 + r, y1, x2 - r, y2, fill=fill, outline="")

    def _handle_draw(self) -> None:
        self.delete("all")
        w = self.winfo_width()
        h = self.winfo_height()
        n = len(self.secenekler)
        if w <= 2 or h <= 2 or n == 0:
            return

        self._draw_pill(0, 0, w, h, TRACK.to_hex())

        pad = _INNER_PAD.to_int()
        pw = w / float(n)
        cy = h / 2
        dim_hex = DIM.to_hex()
        max_idx = max(1, n - 1)

        for i, (metin, deger) in enumerate(self.secenekler):
            x1 = i * pw + pad
            x2 = (i + 1) * pw - pad
            is_selected = deger == self._secili
            if is_selected:
                pill_color = C1.lerp(C2, 0.2 + 0.6 * (i / max_idx)).to_hex()
                self._draw_pill(x1, pad, x2, h - pad, pill_color)
            self.create_text(
                (x1 + x2) / 2,
                cy,
                text=metin,
                font=(FONT, 10, "bold"),
                fill=_TEXT_ACTIVE if is_selected else dim_hex,
            )

    def _handle_L_click(self, event: tk.Event) -> None:
        n = len(self.secenekler)
        if n == 0:
            return
        w = max(1, self.winfo_width())
        idx = max(0, min(n - 1, int(event.x / (w / float(n)))))
        deger = self.secenekler[idx][1]
        if deger != self._secili:
            self._secili = deger
            self._handle_draw()
            if self.komut is not None:
                self.komut(deger)