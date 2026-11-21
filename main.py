import tkinter as tk
from dalga import Uygulama


def main():
    global OLCEK
    try:  # net (bulanik olmayan) yazi icin Windows DPI farkindaligi
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass
    root = tk.Tk()
    OLCEK = root.winfo_fpixels("1i") / 96.0
    Uygulama(root)
    root.mainloop()


if __name__ == "__main__":
    main()