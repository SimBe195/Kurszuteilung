from typing import Any

import customtkinter as ctk


class AssignmentPage(ctk.CTkFrame):
    def __init__(self, master: Any) -> None:
        ctk.CTkFrame.__init__(self, master)
        label = ctk.CTkLabel(self, text="Dies ist die Zuteilungsseite", fg_color="#ff0000")
        label.pack(pady=10, padx=10)
