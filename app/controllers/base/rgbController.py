from typing import Any, Callable, Union
from abc import ABC, abstractmethod
from pydantic import BaseModel

from app.common.rgbdata import RGBData

class DeviceInfo(BaseModel):
    """Tum cihaz turleri (HID, WMI, OpenRGB, Mock) icin ortak temel bilgi modeli."""
    device_id: str  # Benzersiz kimlik (HID icin path/serial, WMI icin instance id, Mock icin "mock-0")
    name: str = "Unknown Device"

    def __repr__(self):
        return f"{self.name} [{self.device_id}]"

class RGBController(ABC):
    def __init__(self, info:DeviceInfo, device_factory:Callable[[], Any]) -> None:
        if not self.matches(info):
            raise ValueError(f"Verilen {info.__class__.__name__} nesnesi {self.__class__.__name__} sınıfı için uygun değil")
        self.info = info
        self._device_factory = device_factory
        self._dev: Any | None = None

    @classmethod
    @abstractmethod
    def matches(cls, info:DeviceInfo) -> bool:
        """Bu surucu verilen DeviceInfo ile eslesiyor mu?"""

    @abstractmethod
    def connect(self) -> bool: ...

    @abstractmethod
    def close(self) -> None: ...

    @abstractmethod
    def send_colors(self, colors: list[RGBData]) -> bool: ...

    def _on_connect(self) -> None:
        """Opsiyonel: Yazilim moduna gecis paketi isteyen klavyeler override eder."""

    def _on_disconnect(self) -> None:
        """Opsiyonel: Donanim moduna donus paketi isteyen klavyeler override eder."""

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, *args):
        self.close()


class ControllerRegistry:
    def __init__(self):
        self._controllers: list[type[RGBController]] = []

    def register(self, controller_cls:type[RGBController]) -> type[RGBController]:
        if controller_cls not in self._controllers:
            self._controllers.append(controller_cls)
        return controller_cls

    def resolve(self, info: DeviceInfo) -> Union[type[RGBController], None]:
        for cls in self._controllers:
            if cls.matches(info):
                return cls
        return None

    
        
    


