import customtkinter as ctk

from . import main_window


def run() -> None:
    ctk.set_appearance_mode("light")

    window = main_window.MainWindow()
    window.mainloop()
