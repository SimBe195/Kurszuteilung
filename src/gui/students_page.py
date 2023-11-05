from typing import Any

import customtkinter as ctk


class StudentsPage(ctk.CTkFrame):
    def __init__(self, master: Any) -> None:
        ctk.CTkFrame.__init__(self, master)
        label = ctk.CTkLabel(self, text="Dies ist die Kinderseite", fg_color="#ff0000")
        label.pack(pady=10, padx=10)
