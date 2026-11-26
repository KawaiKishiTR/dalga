import tkinter as tk
import tkinter.font as tkfont

from app.common.rgbdata import RGBData
from app.locale.manager import LocaleManager
from app.ui.base.mixins import DrawOnInitMixin
from app.ui.common import Px, KART, C1, C2, FONT, DIM, KENAR
from app.ui.ikon import IkonEnum, Ikon

SURUM = "v0.4"
_APP_NAME = "DALGA"  # Uygulama ismi kasitli olarak cevrilmez

_HEIGHT = Px(98)
_PAD = Px(22)
_BADGE_SIZE = Px(52)
_BADGE_INNER_PAD = Px(4)
_CENTER_Y = Px(40)
_TITLE_GAP = Px(16)
_VERSION_GAP = Px(8)
_SUBTITLE_Y = Px(84)
class Baslik(DrawOnInitMixin, tk.Canvas):
    """Ust kisim: rozet + gradyan 'DALGA' + surum."""

    def __init__(self, 
            ebeveyn:tk.Misc, 
            bg:RGBData,
            yukseklik:Px = _HEIGHT
    ) -> None:
        super().__init__(
            ebeveyn, 
            height=yukseklik.to_int(), 
            bg=bg.to_hex(), 
            highlightthickness=0, 
            bd=0
        )

    def _draw_badge(self, pad: int, cy: int, badge_size: int) -> None:
        half = badge_size / 2
        inner = _BADGE_INNER_PAD.to_int()
        kart_hex = KART.to_hex()

        self.create_oval(
            pad, cy - half, pad + badge_size, cy + half,
            fill=kart_hex, outline=C1.to_hex(), width=2,
        )
        self.create_oval(
            pad + inner, cy - half + inner, pad + badge_size - inner, cy + half - inner,
            fill=kart_hex, outline=C2.to_hex(), width=1,
        )
        Ikon.ciz(IkonEnum.DALGA, self, pad + half, cy, badge_size * 0.27, C1, KART)

    def _draw_title(self, start_x: int, cy: int) -> None:
        x = float(start_x)
        max_idx = max(1, len(_APP_NAME) - 1)
        for i, ch in enumerate(_APP_NAME):
            color = C1.lerp(C2, i / max_idx).to_hex()
            self.create_text(x, cy, text=ch, font=self._title_font, fill=color, anchor="w")
            x += self._title_font.measure(ch)

        asc = self._title_font.metrics("ascent")
        desc = self._title_font.metrics("descent")
        baseline_y = cy + (asc - desc) / 2
        self.create_text(
            x + _VERSION_GAP.to_int(),
            baseline_y,
            text=self.surum,
            font=(FONT, 11),
            fill=DIM.to_hex(),
            anchor="sw",
        )

    def _handle_draw(self) -> None:
        self.delete("all")
        w = self.winfo_width()
        h = self.winfo_height()
        if w <= 2 or h <= 2:
            return

        pad = _PAD.to_int()
        badge_size = _BADGE_SIZE.to_int()
        cy = _CENTER_Y.to_int()

        self._draw_badge(pad, cy, badge_size)
        self._draw_title(pad + badge_size + _TITLE_GAP.to_int(), cy)

        self.create_text(
            pad,
            _SUBTITLE_Y.to_int(),
            text=LocaleManager().header.subtitle,
            font=(FONT, 9),
            fill=DIM.to_hex(),
            anchor="w",
        )
        self.create_line(pad, h - 1, w - pad, h - 1, fill=KENAR.to_hex())