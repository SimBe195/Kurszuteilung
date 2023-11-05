from typing import Any

import customtkinter as ctk
from functools import partial


class Sidebar(ctk.CTkFrame):
    def __init__(self, master: Any) -> None:
        super().__init__(master=master, corner_radius=0, fg_color="#666666")

        self.frames: list[ctk.CTkFrame] = []
        self.buttons: list[ctk.CTkButton] = []
        self.current_index = 0

    def add_option(self, text: str, page: ctk.CTkFrame):
        option_index = len(self.frames)
        button = ctk.CTkButton(
            master=self,
            text=text,
            font=ctk.CTkFont(size=22),
            hover_color="#aaaaaa",
            text_color="#000000",
            width=250,
            height=75,
            corner_radius=0,
            command=partial(self.show_frame, idx=option_index),
        )
        button.grid(row=option_index, column=0, sticky="ew")
        # button.pack(fill="x", expand=False)
        page.place(relx=0.0, rely=option_index, relwidth=1.0, relheight=1.0)

        self.buttons.append(button)
        self.frames.append(page)

    def show_frame(self, idx: int = 0):
        for button in self.buttons:
            button.configure(require_redraw=True, fg_color="#888888")

        self.buttons[idx].configure(require_redraw=True, fg_color="#cccccc")
        self.frames[idx].tkraise()

        if self.current_index == idx:
            return
        self._shift_frames_animation(from_idx=self.current_index, to_idx=idx)
        self.current_index = idx

    def _shift_frames_animation(self, from_idx: int, to_idx: int, steps=30):
        shifts = [i / steps * (from_idx - to_idx) for i in range(1, steps + 1)]

        def move_frames(step: int = 0):
            if step >= len(shifts):
                return
            for i, frame in enumerate(self.frames):
                frame.place_configure(rely=i - from_idx + shifts[step])
            self.after(4, move_frames, step + 1)

        move_frames()

    def pack(self):
        super().pack(anchor="nw", side="left", expand=False, fill="y")
