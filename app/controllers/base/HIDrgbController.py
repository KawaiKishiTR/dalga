import hid

from typing import Any, Callable, ClassVar
from abc import ABC

from pydantic import model_validator

from app.controllers.base.rgbController import DeviceInfo, RGBController



class HIDDeviceInfo(DeviceInfo):
    path:bytes                              # cihazı yönetmek için işletim sistemi tarafından ayrılan yol
    vid:int                                 # yapımcı firma spesifik kodu 2 byte
    pid:int                                 # firmanın ürün kodu 2 byte
    usage_page:int                          # arayüzün kategorisi 2 byte
    usage:int                               # usage_page altındaki alt görev
    interface_number:int = -1               # usb arayüz numarası (linux compability için kritik)
    manufacturer_string:str | None = None   # yapımcı firma ismi
    product_string:str | None = None        # ürün ismi
    serial_number:str | None = None         # aynı cihazdan 2 adet varsa ayırt etmek için seri numarası

    @model_validator(mode="before")
    @classmethod
    def _populate_base_fields(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data

        data = dict(data)  # Orijinal sozlugu bozmamak icin kopyala

        # 1. device_id otomatik uretimi (path bytes -> str)
        if not data.get("device_id") and "path" in data:
            raw_path = data["path"]
            data["device_id"] = (
                raw_path.decode("utf-8", errors="replace")
                if isinstance(raw_path, bytes)
                else str(raw_path)
            )

        # 2. name otomatik uretimi (product + manufacturer, yoksa VID:PID)
        if not data.get("name"):
            mfg = (data.get("manufacturer_string") or "").strip()
            prod = (data.get("product_string") or "").strip()

            if prod and mfg and not prod.lower().startswith(mfg.lower()):
                data["name"] = f"{mfg} {prod}"
            elif prod:
                data["name"] = prod
            elif mfg:
                data["name"] = mfg
            else:
                vid = data.get("vid", 0)
                pid = data.get("pid", 0)
                data["name"] = f"HID Device ({vid:04X}:{pid:04X})"

        return data

    @classmethod
    def from_hid_dict(cls, raw: dict[str, Any]) -> "HIDDeviceInfo":
        """hid.enumerate() ciktisini dogrudan HIDDeviceInfo'ya cevirir."""
        return cls(
            path=raw["path"],
            vid=raw["vendor_id"],
            pid=raw["product_id"],
            usage_page=raw.get("usage_page", 0),
            usage=raw.get("usage", 0),
            interface_number=raw.get("interface_number", -1),
            manufacturer_string=raw.get("manufacturer_string"),
            product_string=raw.get("product_string"),
            serial_number=raw.get("serial_number"),
        )



class HIDRGBController(RGBController, ABC):
    """USB-HID tabanli tum klavyeler icin ortak temel sinif."""

    vid: ClassVar[int]
    pid: ClassVar[int]
    usage_page: ClassVar[int | None] = None
    usage: ClassVar[int | None] = None
    interface_number: ClassVar[int | None] = None
    manufacturer_string: ClassVar[str | None] = None
    product_string: ClassVar[str | None] = None

    def __init__(self, info: DeviceInfo, device_factory: Callable[[], Any] = hid.device):
        super().__init__(info, device_factory)

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        if ABC in cls.__bases__:
            return
        if not isinstance(getattr(cls, "vid", None), int):
            raise NotImplementedError(f"{cls.__name__} must define int class variable 'vid'")
        if not isinstance(getattr(cls, "pid", None), int):
            raise NotImplementedError(f"{cls.__name__} must define int class variable 'pid'")

    @classmethod
    def matches(cls, info: HIDDeviceInfo) -> bool:
        if not isinstance(info, HIDDeviceInfo):
            return False
        if info.vid != cls.vid or info.pid != cls.pid:
            return False
        if cls.usage_page is not None and info.usage_page != cls.usage_page:
            return False
        if cls.usage is not None and info.usage != cls.usage:
            return False
        if cls.interface_number is not None and info.interface_number != cls.interface_number:
            return False
        if cls.manufacturer_string is not None and info.manufacturer_string != cls.manufacturer_string:
            return False
        if cls.product_string is not None and info.product_string != cls.product_string:
            return False
        return True

    def connect(self) -> bool:
        if self._dev is not None:
            return True
        dev = self._device_factory()
        try:
            dev.open_path(self.info.path)
            self._dev = dev
            self._on_connect()  # Cihaza ozel handshake varsa burada calisir
            return True
        except OSError:
            return False

    def close(self) -> None:
        if self._dev is None:
            return
        try:
            self._on_disconnect()  # Cihaza ozel kapanis paketi varsa burada calisir
        finally:
            self._dev.close()
            self._dev = None

    def _write(self, data: bytes) -> bool:
        """Alt siniflarin kullanacagi guvenli yazma yardimcisi."""
        if self._dev is None and not self.connect():
            return False
        try:
            if self._dev.write(data) <= 0:
                self.close()
                return False
            return True
        except OSError:
            self.close()
            return False
