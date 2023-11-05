from typing import Any

import customtkinter as ctk


class ErrorPopup(ctk.CTkToplevel):
    def __init__(self, master: Any, text: str) -> None:
        ctk.CTkToplevel.__init__(self, master)
        self.title("Fehler")

        error_title = ctk.CTkLabel(self, text="Fehler!", font=ctk.CTkFont(size=22))
        error_title.grid(row=0, column=0, padx=20, pady=30)

        error_label = ctk.CTkLabel(self, text=text, font=ctk.CTkFont(size=16), wraplength=500)
        error_label.grid(row=1, column=0, padx=20, pady=20, sticky="w")

        close_button = ctk.CTkButton(self, text="Ok", font=ctk.CTkFont(size=16), command=self.destroy)
        close_button.grid(row=2, column=0, padx=20, pady=20)


def open_error_popup(master: Any, text: str) -> None:
    popup = ErrorPopup(master, text)
    popup.tkraise()
    popup.focus_set()
    master.wait_window(popup)
