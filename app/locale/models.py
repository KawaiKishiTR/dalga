from pydantic import BaseModel


class HeaderLocale(BaseModel):
    app_name: str = "DALGA"
    subtitle: str = "Her tuşa bastığında ışık dalgası yayılır"


class StatusLocale(BaseModel):
    stopped: str = "Durdu"
    running: str = "Çalışıyor"
    keyboard_not_found: str = "Klavye bulunamadı. GG / OpenRGB kapalı mı?"
    connection_lost: str = "Bağlantı koptu, yeniden deneniyor..."


class EffectLocale(BaseModel):
    card_title: str = "EFEKT"
    speed: str = "Hız"
    thickness: str = "Kalınlık"
    brightness: str = "Parlaklık"


class ColorLocale(BaseModel):
    card_title: str = "RENK"
    wave_color: str = "Dalga rengi"
    rainbow: str = "Gökkuşağı"
    solid: str = "Sabit renk"
    pick_color: str = "Renk seç"
    dialog_title: str = "Dalga rengi"


class StandbyLocale(BaseModel):
    card_title: str = "BEKLEME IŞIĞI"
    toggle_label: str = "Bekleme ışığı"
    pick_color: str = "Renk seç"
    dialog_title: str = "Bekleme ışığı rengi"
    brightness: str = "Parlaklık"


class ActionLocale(BaseModel):
    start: str = "BAŞLAT"
    stop: str = "DURDUR"


class LocaleSchema(BaseModel):
    header: HeaderLocale = HeaderLocale()
    status: StatusLocale = StatusLocale()
    effect: EffectLocale = EffectLocale()
    color: ColorLocale = ColorLocale()
    standby: StandbyLocale = StandbyLocale()
    actions: ActionLocale = ActionLocale()