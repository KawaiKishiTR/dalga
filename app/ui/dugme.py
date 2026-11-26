import tkinter as tk
import tkinter.font as tkfont
from typing import Callable

from app.common.rgbdata import RGBData
from app.ui.base.mixins import ClickableMixin, DrawOnInitMixin, HoverableMixin
from app.ui.ikon import IkonEnum, Ikon
from app.ui.common import (
    Px, FONT, DEVRE, 
)

_WHITE = RGBData(r=255, g=255, b=255)
_DISABLED_TEXT = RGBData.from_hex("#7a7a92")
_ICON_RADIUS = Px(8)
_ICON_GAP = Px(10)
_GRADIENT_STEP = 3

class Dugme(DrawOnInitMixin, HoverableMixin, ClickableMixin, tk.Canvas):
    """Gradyan kapsul dugme (istege bagli simgeli)."""

    def __init__(self, 
                ebeveyn:tk.Misc, 
                metin:str, 
                komut:Callable[[], None], 
                bg:RGBData, 
                c1:RGBData, 
                c2:RGBData, 
                yukseklik:Px = Px(46), 
                genislik:Px | None = None,
                ikon:IkonEnum=None, 
                font:tkfont.Font | None = None, 
                yazi:RGBData = RGBData.from_hex("#ffffff")
            ):
        self.metin, self.komut = metin, komut
        self.c1, self.c2, self.ikon = c1, c2, ikon
        self.font = font or tkfont.Font(root= ebeveyn, family=FONT, size=12, weight="bold")
        self.yazi = yazi
        self._aktif = True

        kw: dict[str, int] = {"width": genislik.to_int()} if genislik is not None else {}
        super().__init__(
            ebeveyn, 
            height=yukseklik.to_int(), 
            bg=bg.to_hex(), 
            highlightthickness=0, 
            bd=0,
            cursor="hand2", 
            **kw
        )

    @property
    def aktif(self) -> bool:
        return self._aktif

    @aktif.setter
    def aktif(self, value:bool) -> None:
        value = bool(value)
        if self._aktif != value:
            self._aktif = value
            self.configure(cursor="hand2" if value else "")
            self._handle_draw()

    def ayarla(
            self, 
            metin:str | None = None, 
            c1:RGBData | None = None, 
            c2:RGBData | None = None, 
            ikon:IkonEnum | None = None
        ):
        if metin is not None:
            self.metin = metin
        if c1 is not None:
            self.c1 = c1
        if c2 is not None:
            self.c2 = c2
        if ikon is not None:
            self.ikon = ikon
        self._handle_draw()

    def _resolve_colors(self) -> tuple[RGBData, RGBData]:
        if not self._aktif:
            return DEVRE, DEVRE
        if self._hovered:
            return (
                self.c1.lerp(_WHITE, 0.14),
                self.c1.lerp(_WHITE, 0.14),
            )
        return self.c1, self.c1

    def _draw_background(self, w:int, h:int, c1:RGBData, c2:RGBData) -> None:
        self.create_oval(0, 0, h, h, fill=c1.to_hex(), outline="")
        self.create_oval(w - h, 0, w, h, fill=c2.to_hex(), outline="")

        x_start = h // 2
        x_end = w - (h // 2)
        if x_end <= x_start:
            return

        # Duz renk ise (devre disi veya c1 == c2) dongu yerine tek dikdortgen
        if c1 == c2:
            self.create_rectangle(x_start, 0, x_end, h, fill=c1.to_hex(), outline="")
            return

        span = float(x_end - x_start)
        for x in range(x_start, x_end, _GRADIENT_STEP):
            color = c1.lerp(c2, (x - x_start) / span).to_hex()
            self.create_line(x, 0, x, h, fill=color, width=_GRADIENT_STEP + 1)
    
    def _draw_content(self, w: int, h: int, c1: RGBData) -> None:
        text_color = self.yazi if self._aktif else _DISABLED_TEXT
        text_width = self.font.measure(self.metin)
        cy = h / 2

        icon_r = _ICON_RADIUS.to_int()
        icon_gap = _ICON_GAP.to_int()
        content_width = text_width + (2 * icon_r + icon_gap if self.ikon is not None else 0)
        cursor_x = (w - content_width) / 2

        if self.ikon is not None:
            Ikon.ciz(self.ikon, self, cursor_x + icon_r, cy, icon_r, text_color, c1)
            cursor_x += 2 * icon_r + icon_gap

        self.create_text(
            cursor_x,
            cy,
            text=self.metin,
            font=self.font,
            fill=text_color.to_hex(),
            anchor="w",
        )
    
    def _handle_draw(self) -> None:
        self.delete("all")
        w = self.winfo_width()
        h = self.winfo_height()
        if w <= 2 or h <= 2:
            return

        c1, c2 = self._resolve_colors()
        self._draw_background(w, h, c1, c2)
        self._draw_content(w, h, c1)

    def _handle_L_click(self, e):
        if self.aktif and self.komut:
            self.komut()

    def _on_hover_change(self, hovered:bool) -> None:
        self._handle_draw()