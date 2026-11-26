"""
DALGA v0.4 - Apex 3 TKL icin tusa basinca bolgesel dalga efekti (arayuzlu)

Gerekenler:
    - apex_hid.py bu dosyayla AYNI klasorde olmali
    - pip install keyboard   (zaten kurulu)

Calistirmadan once SteelSeries GG ve OpenRGB KAPALI olsun.
Calistir:  python main.py
Ayarlar, ayni klasordeki config/{model_adı}.yml dosyasina otomatik kaydedilir.
"""

import math
import threading
import time
import tkinter as tk
import tkinter.font as tkfont
from collections.abc import Callable
from tkinter import colorchooser

import keyboard

from apex_hid import ApexKlavye
from app.common.file_paths import BASE_DIR
from app.common.rgbdata import RGBData
from app.config.models import AppConfig
from app.locale.manager import LocaleManager
from app.ui.anahtar import Anahtar
from app.ui.baslik import Baslik, SURUM
from app.ui.common import (
    BG, C1, C2, DIM, DUR1, DUR2, FG, FONT, 
    HATA, KART, KENAR, TRACK, YESIL, Px
)
from app.ui.dugme import Dugme
from app.ui.ikon import Ikon, IkonEnum
from app.ui.kaydirici import Kaydirici
from app.ui.ornek import Ornek
from app.ui.segment import Segment

KLASOR = str(BASE_DIR)

# ------------------------- EFEKT SABITLERI -------------------------
BOLGE_SAYISI = 8
TOPLAM_GENISLIK = 18.5  # klavyenin tus genisligi cinsinden toplam genisligi
SOL_BOSLUK = 0.0
MIN_KALINLIK = 0.8      # bunun altinda titreme yapiyor
MIN_OMUR = 0.05
MIN_FPS = 5
HUE_ADIM = 0.06
SIYAH = RGBData(r=0, g=0, b=0)

# ------------------------- ARAYUZ SABITLERI -------------------------
_WIN_WIDTH = Px(780)
_BODY_PAD_X = Px(20)
_BODY_PAD_TOP = Px(14)
_BODY_PAD_BOTTOM = Px(20)
_COL_GAP = Px(9)
_CARD_PAD_X = Px(16)
_CARD_PAD_Y = Px(12)
_ROW_PAD_TOP = Px(10)
_SECTION_GAP = Px(16)
_SPACER_H = Px(14)
_ICON_TEXT_GAP = Px(8)

_MAIN_BTN_H = Px(54)
_SMALL_BTN_H = Px(34)
_SMALL_BTN_W = Px(110)
_STATUS_ICON_SIZE = Px(20)

_SAVE_DEBOUNCE_MS = 400
_STATUS_POLL_MS = 500

_SPEED_RANGE = (2.0, 20.0, 0.5)
_THICKNESS_RANGE = (MIN_KALINLIK, 4.0, 0.1)
_BRIGHTNESS_RANGE = (5.0, 100.0, 1.0)
_STANDBY_BRIGHTNESS_RANGE = (1.0, 100.0, 1.0)


# ------------------------- TUS KONUMLARI -------------------------
# Tusun fiziksel konumu (scan code'a gore; Turkce/Ingilizce Q duzeninde ayni calisir)
KONUM: dict[int, float] = {
    1: 0.5,    # Esc
    87: 12.5,  # F11
    88: 13.5,  # F12
    41: 0.5,   # `
    14: 14.0,  # Backspace
    15: 0.75,  # Tab
    28: 14.0,  # Enter
    58: 0.9,   # Caps
    43: 14.0,
    42: 1.1,   # Sol Shift
    86: 2.0,   # < > tusu
    54: 13.0,  # Sag Shift
    29: 0.7,   # Ctrl
    56: 3.5,   # Alt
    57: 7.0,   # Space
    75: 15.5,  # Sol ok
    80: 16.5,  # Asagi ok
    77: 17.5,  # Sag ok
    72: 16.5,  # Yukari ok
}
for _i, _sc in enumerate(range(59, 69)):  # F1-F10
    KONUM[_sc] = 2.5 + _i * 1.0 + (_i // 4) * 0.5
for _sc in range(2, 14):  # 1 2 3 ... - =
    KONUM[_sc] = 1.5 + (_sc - 2)
for _sc in range(16, 28):  # Q W E ... [ ]
    KONUM[_sc] = 2.0 + (_sc - 16)
for _sc in range(30, 42):  # A S D ... ; '
    KONUM[_sc] = 2.25 + (_sc - 30)
for _sc in range(44, 54):  # Z X C ... . /
    KONUM[_sc] = 2.75 + (_sc - 44)


WaveItem = tuple[float, float, RGBData]


def bolge_bul(scan_code: int):
    x = KONUM.get(scan_code)
    if x is None:
        return None
    oran = (x - SOL_BOSLUK) / TOPLAM_GENISLIK
    return min(max(oran * BOLGE_SAYISI, 0), BOLGE_SAYISI - 1e-6)


def bekleme_rengi(ayar: AppConfig) -> RGBData:
    """Bekleme isigi aciksa (R,G,B) float, kapaliysa siyah."""
    if not ayar.bekleme_acik:
        return SIYAH
    return ayar.bekleme_renk * (ayar.bekleme_parlaklik / 100.0)


def kare_hesapla(aktif: list[WaveItem], simdi: float, ayar: AppConfig) -> list[RGBData]:
    """Verilen dalgalar icin 8 bolgenin RGBData degerlerini hesaplar."""
    n = BOLGE_SAYISI
    hiz = float(ayar.hiz)
    kalinlik = max(MIN_KALINLIK, float(ayar.kalinlik))
    omur = max(MIN_OMUR, float(ayar.omur))
    parlaklik = max(0.0, min(1.0, float(ayar.parlaklik) / 100.0))
    taban = bekleme_rengi(ayar)
    toplam = [list(taban.to_tuple()) for _ in range(n)]

    for merkez, basla, renk in aktif:
        yas = simdi - basla
        yaricap = yas * hiz
        sonum = math.exp(-yas / omur)
        for z in range(n):
            mesafe = abs((z + 0.5) - merkez)
            fark = abs(mesafe - yaricap)
            siddet = max(0.0, 1.0 - fark / kalinlik)
            if yas < 0.08 and mesafe < 0.8:  # basilan yer ilk anda parlasin
                siddet = 1.0
            v = siddet * sonum * parlaklik
            toplam[z][0] += renk.r * v
            toplam[z][1] += renk.g * v
            toplam[z][2] += renk.b * v

    return [RGBData(r=int(c[0]), g=int(c[1]), b=int(c[2])) for c in toplam]


# ------------------------------ MOTOR ------------------------------
class Motor:
    """Tus dinler, dalgalari hesaplar, klavyeye gonderir (arka planda)."""

    def __init__(self, ayar: AppConfig) -> None:
        self.ayar = ayar
        self.kb = ApexKlavye()
        self.kilit = threading.Lock()
        self.dalgalar: list[WaveItem] = []
        self.hue = 0.0
        self.durdur_ev = threading.Event()
        self.thread: threading.Thread | None = None
        self._hook: object | None = None
        self.calisiyor = False
        self.durum = LocaleManager().status.stopped
        self.durum_hata = False

    def _renk_sec(self) -> RGBData:
        if self.ayar.mod == "sabit":
            return self.ayar.renk
        self.hue = (self.hue + HUE_ADIM) % 1.0
        return RGBData.from_hsv(self.hue, 1.0, 1.0)

    def _tus(self, olay: keyboard.KeyboardEvent) -> None:
        if olay.event_type != "down":
            return
        merkez = bolge_bul(olay.scan_code)
        if merkez is None:
            return
        with self.kilit:
            self.dalgalar.append((merkez, time.time(), self._renk_sec()))
            del self.dalgalar[: -max(1, int(self.ayar.max_dalga))]

    def baslat(self):
        if self.calisiyor:
            return True
        if not self.kb.baglan():
            self.durum = LocaleManager().status.keyboard_not_found
            self.durum_hata = True
            return False
        with self.kilit:
            self.dalgalar.clear()
        self.durdur_ev.clear()
        self._hook = keyboard.hook(self._tus)
        self.thread = threading.Thread(target=self._dongu, daemon=True)
        self.thread.start()
        self.calisiyor = True
        self.durum = LocaleManager().status.running
        self.durum_hata = False
        return True

    def durdur(self) -> None:
        if not self.calisiyor:
            return
        self.durdur_ev.set()
        if self.thread is not None:
            self.thread.join(timeout=2)
        if self._hook is not None:
            try:
                keyboard.unhook(self._hook)
            except Exception:
                pass
            self._hook = None
        try:
            self.kb.renk_gonder([SIYAH] * BOLGE_SAYISI)
        except Exception:
            pass
        self.kb.kapat()
        self.calisiyor = False
        self.durum = LocaleManager().status.stopped
        self.durum_hata = False

    def _dongu(self) -> None:
        son_gonderilen: list[RGBData] | None = None
        while not self.durdur_ev.is_set():
            t0 = time.time()
            aralik = 1.0 / max(MIN_FPS, int(self.ayar.fps))
            omur = max(MIN_OMUR, float(self.ayar.omur))
            with self.kilit:
                self.dalgalar[:] = [d for d in self.dalgalar if t0 - d[1] < omur * 2.5]
                aktif = list(self.dalgalar)

            kare = kare_hesapla(aktif, t0, self.ayar)

            if kare != son_gonderilen:
                if self.kb.renk_gonder(kare):
                    son_gonderilen = kare
                    self.durum = LocaleManager().status.running
                    self.durum_hata = False
                else:
                    self.durum = LocaleManager().status.connection_lost
                    self.durum_hata = True
                    son_gonderilen = None
                    self.durdur_ev.wait(0.5)

            gecen = time.time() - t0
            if gecen < aralik:
                self.durdur_ev.wait(aralik - gecen)

# ----------------------------- ARAYUZ -----------------------------
class Uygulama:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.ayar: AppConfig = AppConfig.get_config()
        LocaleManager.set_language(self.ayar.dil)
        self.motor = Motor(self.ayar)
        self._kayit_zamanlayici: str | None = None
        self._small_btn_font = tkfont.Font(root=root, family=FONT, size=10, weight="bold")

        root.title(f"DALGA {SURUM}")
        root.configure(bg=BG.to_hex())
        root.resizable(False, False)

        Baslik(root, BG).pack(fill="x")

        govde = tk.Frame(root, bg=BG.to_hex())
        govde.pack(
            fill="both",
            expand=True,
            padx=_BODY_PAD_X.to_int(),
            pady=(_BODY_PAD_TOP.to_int(), _BODY_PAD_BOTTOM.to_int()),
        )
        govde.columnconfigure(0, weight=1, uniform="k")
        govde.columnconfigure(1, weight=1, uniform="k")

        sol = tk.Frame(govde, bg=BG.to_hex())
        sol.grid(row=0, column=0, sticky="nsew", padx=(0, _COL_GAP.to_int()))
        sag = tk.Frame(govde, bg=BG.to_hex())
        sag.grid(row=0, column=1, sticky="nsew", padx=(_COL_GAP.to_int(), 0))

        self._build_left_column(sol)
        self._build_right_column(sag)
        self._gorunum_senkron()

        root.update_idletasks()
        root.geometry(f"{_WIN_WIDTH.to_int()}x{root.winfo_reqheight()}")
        root.protocol("WM_DELETE_WINDOW", self._kapat)
        self._durum_guncelle()
    def _build_left_column(self, parent: tk.Frame) -> None:
        loc = LocaleManager()
        bg_hex = BG.to_hex()
        kart_hex = KART.to_hex()
        dim_hex = DIM.to_hex()

        k1 = self._kart(parent, loc.effect.card_title)
        self._kaydirici_satiri(
            k1, IkonEnum.HIZ, loc.effect.speed, "hiz",
            *_SPEED_RANGE, lambda v: f"{v:.1f}", False,
        )
        self._kaydirici_satiri(
            k1, IkonEnum.KALINLIK, loc.effect.thickness, "kalinlik",
            *_THICKNESS_RANGE, lambda v: f"{v:.1f}", False,
        )
        self._kaydirici_satiri(
            k1, IkonEnum.PARLAKLIK, loc.effect.brightness, "parlaklik",
            *_BRIGHTNESS_RANGE, lambda v: f"%{int(v)}", True,
        )
        tk.Frame(k1, height=_SPACER_H.to_int(), bg=kart_hex).pack()

        self.ana = Dugme(
            parent, loc.actions.start, self._ac_kapat, BG, C1, C2,
            yukseklik=_MAIN_BTN_H, ikon=IkonEnum.OYNAT,
        )
        self.ana.pack(fill="x", pady=(_SECTION_GAP.to_int(), 0))

        durum_satiri = tk.Frame(parent, bg=bg_hex)
        durum_satiri.pack(fill="x", pady=(_CARD_PAD_Y.to_int(), 0))
        Ikon(durum_satiri, IkonEnum.KLAVYE, boyut=_STATUS_ICON_SIZE).pack(side="left")
        self.nokta = tk.Label(durum_satiri, text="●", font=(FONT, 9), fg=dim_hex, bg=bg_hex)
        self.nokta.pack(side="left", padx=(_ICON_TEXT_GAP.to_int(), Px(2).to_int()))
        self.durum = tk.Label(durum_satiri, text=loc.status.stopped, font=(FONT, 9), fg=dim_hex, bg=bg_hex)
        self.durum.pack(side="left")

    def _build_right_column(self, parent: tk.Frame) -> None:
        loc = LocaleManager()
        kart_hex = KART.to_hex()
        fg_hex = FG.to_hex()
        pad_x = _CARD_PAD_X.to_int()
        row_top = _ROW_PAD_TOP.to_int()
        card_y = _CARD_PAD_Y.to_int()

        # Renk karti
        k2 = self._kart(parent, loc.color.card_title)
        satir = tk.Frame(k2, bg=kart_hex)
        satir.pack(fill="x", padx=pad_x, pady=(row_top, 0))
        Ikon(satir, IkonEnum.RENK).pack(side="left")
        tk.Label(satir, text=loc.color.wave_color, font=(FONT, 10, "bold"), fg=fg_hex, bg=kart_hex).pack(
            side="left", padx=(_ICON_TEXT_GAP.to_int(), 0),
        )

        self.segment: Segment[str] = Segment(
            k2,
            [(loc.color.rainbow, "gokkusagi"), (loc.color.solid, "sabit")],
            self.ayar.mod,
            self._mod_degisti,
            KART,
        )
        self.segment.pack(fill="x", padx=pad_x, pady=(row_top, 0))

        renk_satir = tk.Frame(k2, bg=kart_hex)
        renk_satir.pack(fill="x", padx=pad_x, pady=(card_y, pad_x))
        self.ornek = Ornek(renk_satir, self.ayar.renk, self._renk_sec, KART)
        self.ornek.pack(side="left")
        self.renk_dugme = Dugme(
            renk_satir, loc.color.pick_color, self._renk_sec, KART, TRACK, TRACK,
            yukseklik=_SMALL_BTN_H, genislik=_SMALL_BTN_W, font=self._small_btn_font, yazi=FG,
        )
        self.renk_dugme.pack(side="left", padx=(card_y, 0))

        # Bekleme karti
        k3 = self._kart(parent, loc.standby.card_title, ust_bosluk=_SECTION_GAP)
        satir = tk.Frame(k3, bg=kart_hex)
        satir.pack(fill="x", padx=pad_x, pady=(row_top, 0))
        Ikon(satir, IkonEnum.AY).pack(side="left")
        tk.Label(satir, text=loc.standby.toggle_label, font=(FONT, 10, "bold"), fg=fg_hex, bg=kart_hex).pack(
            side="left", padx=(_ICON_TEXT_GAP.to_int(), 0),
        )
        self.bek_anahtar = Anahtar(satir, self.ayar.bekleme_acik, self._bek_ac, KART)
        self.bek_anahtar.pack(side="right")

        bek_satir = tk.Frame(k3, bg=kart_hex)
        bek_satir.pack(fill="x", padx=pad_x, pady=(card_y, 0))
        self.bek_ornek = Ornek(bek_satir, self.ayar.bekleme_renk, self._bek_renk_sec, KART)
        self.bek_ornek.pack(side="left")
        self.bek_dugme = Dugme(
            bek_satir, loc.standby.pick_color, self._bek_renk_sec, KART, TRACK, TRACK,
            yukseklik=_SMALL_BTN_H, genislik=_SMALL_BTN_W, font=self._small_btn_font, yazi=FG,
        )
        self.bek_dugme.pack(side="left", padx=(card_y, 0))

        self.bek_slider, _ = self._kaydirici_satiri(
            k3, IkonEnum.PARLAKLIK, loc.standby.brightness, "bekleme_parlaklik",
            *_STANDBY_BRIGHTNESS_RANGE, lambda v: f"%{int(v)}", True,
        )
        tk.Frame(k3, height=_SPACER_H.to_int(), bg=kart_hex).pack()

    # --- yapi tasi ---
    def _kart(self, ebeveyn: tk.Misc, baslik: str, ust_bosluk: Px = Px(0)) -> tk.Frame:
        kart_hex = KART.to_hex()
        kenar_hex = KENAR.to_hex()
        kart = tk.Frame(
            ebeveyn, bg=kart_hex, highlightbackground=kenar_hex,
            highlightcolor=kenar_hex, highlightthickness=1,
        )
        kart.pack(fill="x", pady=(ust_bosluk.to_int(), 0))
        tk.Label(
            kart, text=baslik, font=(FONT, 8, "bold"),
            fg=DIM.to_hex(), bg=kart_hex, anchor="w",
        ).pack(fill="x", padx=_CARD_PAD_X.to_int(), pady=(_CARD_PAD_Y.to_int(), 0))
        return kart
    
    def _kaydirici_satiri(
        self,
        kart: tk.Frame,
        ikon: IkonEnum,
        ad: str,
        anahtar: str,
        alt: float,
        ust: float,
        adim: float,
        bicim: Callable[[float], str],
        tamsayi: bool,
    ) -> tuple[Kaydirici, tk.Label]:
        kart_hex = KART.to_hex()
        cerceve = tk.Frame(kart, bg=kart_hex)
        cerceve.pack(fill="x", padx=_CARD_PAD_X.to_int(), pady=(_ROW_PAD_TOP.to_int(), 0))

        ust_satir = tk.Frame(cerceve, bg=kart_hex)
        ust_satir.pack(fill="x")
        Ikon(ust_satir, ikon).pack(side="left")
        tk.Label(ust_satir, text=ad, font=(FONT, 10, "bold"), fg=FG.to_hex(), bg=kart_hex).pack(
            side="left", padx=(_ICON_TEXT_GAP.to_int(), 0),
        )

        mevcut = float(getattr(self.ayar, anahtar))
        deger_lbl = tk.Label(ust_satir, text=bicim(mevcut), font=(FONT, 10, "bold"), fg=C1.to_hex(), bg=kart_hex)
        deger_lbl.pack(side="right")

        def degisti(v: float) -> None:
            temiz: int | float = int(round(v)) if tamsayi else round(float(v), 2)
            setattr(self.ayar, anahtar, temiz)
            deger_lbl.config(text=bicim(float(temiz)))
            self._kaydet_planla()

        slider = Kaydirici(cerceve, alt, ust, adim, mevcut, degisti, KART)
        slider.pack(fill="x", pady=(Px(2).to_int(), 0))
        return slider, deger_lbl

    # --- gorunum / olaylar ---
    def _gorunum_senkron(self) -> None:
        sabit = self.ayar.mod == "sabit"
        self.ornek.gokkusagi = not sabit
        self.ornek.renk = self.ayar.renk
        self.renk_dugme.aktif = sabit

        acik = self.ayar.bekleme_acik
        self.bek_ornek.aktif = acik
        self.bek_ornek.renk = self.ayar.bekleme_renk
        self.bek_dugme.aktif = acik
        self.bek_slider.aktif = acik

    def _kaydet_planla(self) -> None:
        if self._kayit_zamanlayici is not None:
            self.root.after_cancel(self._kayit_zamanlayici)
        self._kayit_zamanlayici = self.root.after(_SAVE_DEBOUNCE_MS, self.ayar.set_config)

    def _mod_degisti(self, deger: str) -> None:
        self.ayar.mod = deger
        self._gorunum_senkron()
        self._kaydet_planla()

    def _renk_sec(self) -> None:
        sonuc = colorchooser.askcolor(
            color=self.ayar.renk.to_hex(),
            title=LocaleManager().color.dialog_title,
        )
        if sonuc and sonuc[1]:
            self.ayar.renk = RGBData.from_hex(sonuc[1])
            self._gorunum_senkron()
            self._kaydet_planla()

    def _bek_ac(self, deger: bool) -> None:
        self.ayar.bekleme_acik = bool(deger)
        self._gorunum_senkron()
        self._kaydet_planla()

    def _bek_renk_sec(self) -> None:
        if not self.ayar.bekleme_acik:
            return
        sonuc = colorchooser.askcolor(
            color=self.ayar.bekleme_renk.to_hex(),
            title=LocaleManager().standby.dialog_title,
        )
        if sonuc and sonuc[1]:
            self.ayar.bekleme_renk = RGBData.from_hex(sonuc[1])
            self._gorunum_senkron()
            self._kaydet_planla()

    def _ac_kapat(self) -> None:
        if self.motor.calisiyor:
            self.motor.durdur()
        else:
            self.motor.baslat()

        loc = LocaleManager().actions
        if self.motor.calisiyor:
            self.ana.ayarla(metin=loc.stop, c1=DUR1, c2=DUR2, ikon=IkonEnum.DURDUR)
        else:
            self.ana.ayarla(metin=loc.start, c1=C1, c2=C2, ikon=IkonEnum.OYNAT)

    def _durum_guncelle(self) -> None:
        if self.motor.durum_hata:
            nokta_renk = yazi_renk = HATA.to_hex()
        elif self.motor.calisiyor:
            nokta_renk = YESIL.to_hex()
            yazi_renk = FG.to_hex()
        else:
            nokta_renk = yazi_renk = DIM.to_hex()

        self.nokta.config(fg=nokta_renk)
        self.durum.config(text=self.motor.durum, fg=yazi_renk)
        self.root.after(_STATUS_POLL_MS, self._durum_guncelle)

    def _kapat(self) -> None:
        try:
            self.motor.durdur()
        finally:
            self.ayar.set_config()
            self.root.destroy()