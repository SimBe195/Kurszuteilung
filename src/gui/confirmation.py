from typing import Any

import customtkinter as ctk


class ConfirmationDialog(ctk.CTkToplevel):
    def __init__(self, master: Any, text: str) -> None:
        ctk.CTkToplevel.__init__(self, master)

        self.title("Bestätigung")
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        label = ctk.CTkLabel(self, wraplength=300, text=text, font=ctk.CTkFont(size=14))
        label.grid(row=0, column=0, columnspan=2, padx=10, pady=30, sticky="ew")

        self.choice_var = ctk.BooleanVar()

        accept_button = ctk.CTkButton(self, text="Akzeptieren", font=ctk.CTkFont(size=16), command=self.on_accept)
        accept_button.grid(row=1, column=0, padx=30, pady=20)

        cancel_button = ctk.CTkButton(self, text="Abbrechen", font=ctk.CTkFont(size=16), command=self.on_cancel)
        cancel_button.grid(row=1, column=1, padx=30, pady=20)

    def on_accept(self):
        self.choice_var.set(True)
        self.destroy()

    def on_cancel(self):
        self.choice_var.set(False)
        self.destroy()


def confirm_choice(master: Any, text: str) -> bool:
    dialog = ConfirmationDialog(master, text)
    dialog.after(50, lambda: dialog.focus_set())
    master.wait_window(dialog)

    return dialog.choice_var.get()
