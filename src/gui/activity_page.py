from typing import Any

import customtkinter as ctk
from tkinter import ttk

from activity import Activity
from gui.confirmation import confirm_choice
from gui.error_popup import open_error_popup
from gui.search_dialog import search_activity
from state import State


class ActivityPage(ctk.CTkFrame):
    def __init__(self, master: Any) -> None:
        ctk.CTkFrame.__init__(self, master)

        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(self, text="Kurse", font=ctk.CTkFont(size=32))
        title.grid(row=0, column=0, padx=20, pady=(20, 0), sticky="w")

        separator = ttk.Separator(self, orient="horizontal")
        separator.grid(row=1, column=0, padx=10, pady=20, sticky="ew")

        button_frame = ctk.CTkFrame(self, fg_color=self.cget("fg_color"))
        button_frame.grid(row=2, column=0, padx=20, sticky="w")
        add_activity_button = ctk.CTkButton(
            button_frame, text="Hinzufügen", font=ctk.CTkFont(size=18), command=self.add_activity
        )
        add_activity_button.grid(row=0, column=0, padx=10)

        edit_activity_button = ctk.CTkButton(
            button_frame, text="Bearbeiten", font=ctk.CTkFont(size=18), command=self.edit_activity
        )
        edit_activity_button.grid(row=0, column=1, padx=10)

        edit_activity_button = ctk.CTkButton(
            button_frame, text="Entfernen", font=ctk.CTkFont(size=18), command=self.remove_activity
        )
        edit_activity_button.grid(row=0, column=2, padx=10)

        self.activity_view = ctk.CTkScrollableFrame(self)
        self.activity_view.grid(row=3, column=0, padx=20, pady=30, sticky="nsew")

        for idx, title in enumerate(["ID", "Bezeichnung", "Betreuung", "Min. Teiln.", "Max. Teiln.", "Klassen"]):
            column_title = ctk.CTkLabel(self.activity_view, text=title, font=ctk.CTkFont(size=20))
            column_title.grid(row=0, column=idx, padx=20)

        self.display_activities()

    def add_activity(self):
        dialog = ModifyActivityDialog(self, title="Kurs hinzufügen")
        dialog.tkraise()
        dialog.focus_set()
        self.wait_window(dialog)
        self.display_activities()

    def edit_activity(self):
        if (activity := search_activity(self)) is None:
            return
        dialog = ModifyActivityDialog(self, title="Kurs bearbeiten")
        dialog.insert_activity_data(activity)
        dialog.tkraise()
        dialog.focus_set()
        self.wait_window(dialog)
        self.display_activities()

    def remove_activity(self):
        if (activity := search_activity(self)) is not None:
            if confirm_choice(self, f'Kurs "{activity.name}" wirklich entfernen?'):
                State().remove_activity_by_id(activity.id)
                self.display_activities()

    def display_activities(self):
        for widget in self.activity_view.winfo_children():
            if widget.grid_info()["row"] > 0:
                widget.destroy()

        state = State()
        for row, activity in enumerate(state.activities, start=1):
            id_label = ctk.CTkLabel(self.activity_view, text=str(activity.id), font=ctk.CTkFont(size=16))
            id_label.grid(row=row, column=0, pady=5, sticky="nsew")

            name_label = ctk.CTkLabel(self.activity_view, text=activity.name, font=ctk.CTkFont(size=16))
            name_label.grid(row=row, column=1, pady=5, sticky="nsew")

            supervisor_label = ctk.CTkLabel(self.activity_view, text=activity.supervisor, font=ctk.CTkFont(size=16))
            supervisor_label.grid(row=row, column=2, pady=5, sticky="nsew")

            min_capacity_label = ctk.CTkLabel(
                self.activity_view, text=str(activity.min_capacity), font=ctk.CTkFont(size=16)
            )
            min_capacity_label.grid(row=row, column=3, pady=5, sticky="nsew")

            max_capacity_label = ctk.CTkLabel(
                self.activity_view, text=str(activity.max_capacity), font=ctk.CTkFont(size=16)
            )
            max_capacity_label.grid(row=row, column=4, pady=5, sticky="nsew")

            grades_text = ", ".join([str(grade) for grade in range(1, 5) if activity.is_valid_grade(grade)])
            grades_label = ctk.CTkLabel(self.activity_view, text=grades_text, font=ctk.CTkFont(size=16))
            grades_label.grid(row=row, column=5, pady=5, sticky="nsew")


class ModifyActivityDialog(ctk.CTkToplevel):
    def __init__(self, master: Any, title: str) -> None:
        ctk.CTkToplevel.__init__(self, master)

        self.title(title)

        self.grid_columnconfigure(0, weight=1)

        name_frame = ctk.CTkFrame(self)
        name_frame.grid_columnconfigure(1, weight=1)
        name_frame.grid(row=0, column=0, sticky="we")
        name_label = ctk.CTkLabel(name_frame, text="Bezeichnung:", font=ctk.CTkFont(size=16))
        name_label.grid(row=0, column=0, padx=20, pady=20, sticky="w")
        self.name_entry = ctk.CTkEntry(name_frame)
        self.name_entry.grid(row=0, column=1, padx=20, pady=20, sticky="we")

        supervisor_frame = ctk.CTkFrame(self)
        supervisor_frame.grid_columnconfigure(1, weight=1)
        supervisor_frame.grid(row=1, column=0, sticky="we")
        supervisor_label = ctk.CTkLabel(supervisor_frame, text="Betreuung:", font=ctk.CTkFont(size=16))
        supervisor_label.grid(row=0, column=0, padx=20, pady=20, sticky="w")
        self.supervisor_entry = ctk.CTkEntry(supervisor_frame)
        self.supervisor_entry.grid(row=0, column=1, padx=20, pady=20, sticky="we")

        capacity_frame = ctk.CTkFrame(self)
        capacity_frame.grid_columnconfigure(0, weight=1)
        capacity_frame.grid(row=2, column=0, sticky="we")
        capacity_label = ctk.CTkLabel(capacity_frame, text="Teilnehmerzahl:", font=ctk.CTkFont(size=16))
        capacity_label.grid(row=0, column=0, columnspan=2, padx=20, pady=20, sticky="w")
        self.min_capacity_label = ctk.CTkLabel(capacity_frame, font=ctk.CTkFont(size=14))
        self.min_capacity_label.grid(row=1, column=0, padx=20, sticky="w")
        self.min_capacity_var = ctk.IntVar()
        min_capacity_slider = ctk.CTkSlider(
            capacity_frame,
            from_=1,
            to=50,
            number_of_steps=50,
            variable=self.min_capacity_var,
            command=lambda _: self.update_capacity_labels(),
        )
        self.min_capacity_var.set(value=1)
        min_capacity_slider.grid(row=1, column=1, padx=20)
        self.max_capacity_label = ctk.CTkLabel(capacity_frame, font=ctk.CTkFont(size=14))
        self.max_capacity_label.grid(row=2, column=0, padx=20, sticky="w")
        self.max_capacity_var = ctk.IntVar()
        max_capacity_slider = ctk.CTkSlider(
            capacity_frame,
            from_=1,
            to=50,
            number_of_steps=50,
            variable=self.max_capacity_var,
            command=lambda _: self.update_capacity_labels(),
        )
        self.max_capacity_var.set(50)
        max_capacity_slider.grid(row=2, column=1, padx=20)

        self.update_capacity_labels()

        valid_grades_frame = ctk.CTkFrame(self)
        valid_grades_frame.grid_columnconfigure(0, weight=1)
        valid_grades_frame.grid(row=3, column=0, sticky="we")
        valid_grades_label = ctk.CTkLabel(valid_grades_frame, text="Klassen:", font=ctk.CTkFont(size=16))
        valid_grades_label.grid(row=0, column=0, columnspan=4, padx=20, pady=20, sticky="w")
        self.valid_grades_check_vars: list[ctk.BooleanVar] = []
        for grade in range(1, 5):
            check_var = ctk.BooleanVar(value=True)
            grade_checkbox = ctk.CTkCheckBox(
                valid_grades_frame, text=str(grade), variable=check_var, onvalue=True, offvalue=False
            )
            grade_checkbox.grid(row=1, column=grade - 1, padx=(20, 0), pady=10)
            self.valid_grades_check_vars.append(check_var)

        button_frame = ctk.CTkFrame(self)
        button_frame.grid(row=4, column=0, sticky="we")
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)
        accept_button = ctk.CTkButton(button_frame, text="Akzeptieren", command=self.on_accept)
        accept_button.grid(row=0, column=0, padx=20, pady=20)

        cancel_button = ctk.CTkButton(button_frame, text="Abbrechen", command=self.destroy)
        cancel_button.grid(row=0, column=1, padx=20, pady=20)

        self.current_activity: Activity | None = None

    def update_capacity_labels(self):
        self.min_capacity_label.configure(text=f"Min.\t{self.min_capacity_var.get():>2}")
        self.max_capacity_label.configure(text=f"Max.\t{self.max_capacity_var.get():>2}")

    def insert_activity_data(self, activity: Activity):
        self.current_activity = activity
        self.name_entry.insert(0, activity.name)
        self.supervisor_entry.insert(0, activity.supervisor)
        self.min_capacity_var.set(activity.min_capacity)
        self.max_capacity_var.set(activity.max_capacity)
        for check_var, valid in zip(self.valid_grades_check_vars, activity.valid_grades):
            check_var.set(valid)
        self.update_capacity_labels()

    def on_accept(self):
        state = State()
        name = self.name_entry.get()
        supervisor = self.supervisor_entry.get()
        min_capacity = self.min_capacity_var.get()
        max_capacity = self.max_capacity_var.get()
        valid_grades = [check_var.get() for check_var in self.valid_grades_check_vars]

        if min_capacity > max_capacity:
            open_error_popup(self, "Min. Teilnehmerzahl muss kleiner sein als max. Teilnehmerzahl!")
            return

        if self.current_activity is not None:
            self.current_activity.name = name
            self.current_activity.supervisor = supervisor
            self.current_activity.min_capacity = min_capacity
            self.current_activity.max_capacity = max_capacity
            self.current_activity.valid_grades = valid_grades
        else:
            state.add_activity(
                Activity(
                    name=name,
                    supervisor=supervisor,
                    min_capacity=min_capacity,
                    max_capacity=max_capacity,
                    valid_grades=valid_grades,
                )
            )
        self.destroy()
