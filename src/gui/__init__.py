from . import main_window
import customtkinter as ctk


def run() -> None:
    ctk.set_appearance_mode("light")

    window = main_window.MainWindow()
    window.mainloop()
