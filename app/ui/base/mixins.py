from abc import ABC, abstractmethod
import tkinter as tk

class NeedsTKBaseMixin:
    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        if ABC in cls.__bases__:
            return
        if not issubclass(cls, tk.Misc):
            raise TypeError(f"{cls.__name__} must inherit from a Tkinter widget to use {NeedsTKBaseMixin} based mixins")

class DrawOnInitMixin(NeedsTKBaseMixin, ABC):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bind("<Configure>", lambda e: self._handle_draw())

    @abstractmethod
    def _handle_draw(self) -> None: ...

    def draw(self):
        self._handle_draw()

class HoverableMixin(NeedsTKBaseMixin, ABC):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._hovered:bool = False
        self.bind("<Enter>", self._handle_enter)
        self.bind("<Leave>", self._handle_leave)

    def _handle_enter(self, event:tk.Event) -> None:
        self._hovered = True
        self._on_hover_change(True)

    def _handle_leave(self, event:tk.Event) -> None:
        self._hovered = False
        self._on_hover_change(False)

    @abstractmethod
    def _on_hover_change(self, hovered:bool) -> None: ...

class ClickableMixin(NeedsTKBaseMixin, ABC):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bind("<Button-1>", self._handle_L_click)

    @abstractmethod
    def _handle_L_click(self, event: tk.Event): ...