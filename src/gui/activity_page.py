import copy
from typing import Any

import customtkinter as ctk
from tkinter import ttk

from activity import Activity, Timespan, WEEKDAYS
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

        split_activity_button = ctk.CTkButton(
            button_frame, text="Aufspalten", font=ctk.CTkFont(size=18), command=self.split_activity
        )
        split_activity_button.grid(row=0, column=3, padx=10)

        self.activity_view = ctk.CTkScrollableFrame(self)
        self.activity_view.grid(row=3, column=0, padx=20, pady=30, sticky="nsew")

        for idx, title in enumerate(["ID", "Bezeichnung", "Min. TN.", "Max. TN.", "Zeitslot", "Ersttermin", "Klassen"]):
            column_title = ctk.CTkLabel(self.activity_view, text=title, font=ctk.CTkFont(size=20))
            column_title.grid(row=0, column=idx, padx=20)

        self.display_activities()

    def add_activity(self):
        dialog = ModifyActivityDialog(self, title="Kurs hinzufügen")
        dialog.after(50, lambda: dialog.focus_set())
        self.wait_window(dialog)
        self.display_activities()

    def edit_activity(self):
        if (activity := search_activity(self)) is None:
            return
        dialog = ModifyActivityDialog(self, title="Kurs bearbeiten")
        dialog.insert_activity_data(activity)
        dialog.after(50, lambda: dialog.focus_set())
        self.wait_window(dialog)
        self.display_activities()

    def remove_activity(self):
        if (activity := search_activity(self)) is not None:
            if confirm_choice(self, f'Kurs "{activity.name}" wirklich entfernen?'):
                State().remove_activity_by_id(activity.id)
                self.display_activities()

    def split_activity(self):
        if (activity := search_activity(self)) is not None:
            if not confirm_choice(self, f'Kurs "{activity.name}" wirklich aufspalten?'):
                return

            activity_2 = Activity(
                name=f"{activity.name} 2",
                min_capacity=activity.min_capacity,
                max_capacity=activity.max_capacity,
                timespan=activity.timespan,
                first_date=activity.first_date,
                valid_grades=copy.deepcopy(activity.valid_grades),
            )
            State().add_activity(activity_2)
            for student in State().students:
                if activity.id in student.preferences:
                    student.preferences.append(activity_2.id)

            activity.name = f"{activity.name} 1"

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

            min_capacity_label = ctk.CTkLabel(
                self.activity_view, text=str(activity.min_capacity), font=ctk.CTkFont(size=16)
            )
            min_capacity_label.grid(row=row, column=2, pady=5, sticky="nsew")

            max_capacity_label = ctk.CTkLabel(
                self.activity_view, text=str(activity.max_capacity), font=ctk.CTkFont(size=16)
            )
            max_capacity_label.grid(row=row, column=3, pady=5, sticky="nsew")

            timespan_label = ctk.CTkLabel(self.activity_view, text=str(activity.timespan), font=ctk.CTkFont(size=16))
            timespan_label.grid(row=row, column=4, pady=5, sticky="nsew")

            first_date_label = ctk.CTkLabel(
                self.activity_view, text=str(activity.first_date), font=ctk.CTkFont(size=16)
            )
            first_date_label.grid(row=row, column=5, pady=5, sticky="nsew")

            grades_text = ", ".join([str(grade) for grade in range(1, 5) if activity.is_valid_grade(grade)])
            grades_label = ctk.CTkLabel(self.activity_view, text=grades_text, font=ctk.CTkFont(size=16))
            grades_label.grid(row=row, column=6, pady=5, sticky="nsew")


class ModifyActivityDialog(ctk.CTkToplevel):
    def __init__(self, master: Any, title: str) -> None:
        ctk.CTkToplevel.__init__(self, master)

        self.title(title)

        self.grid_columnconfigure(0, weight=1)

        current_row = 0

        name_frame = ctk.CTkFrame(self)
        name_frame.grid_columnconfigure(1, weight=1)
        name_frame.grid(row=current_row, column=0, sticky="we")
        current_row += 1
        name_label = ctk.CTkLabel(name_frame, text="Bezeichnung:", font=ctk.CTkFont(size=16))
        name_label.grid(row=0, column=0, padx=20, pady=20, sticky="w")
        self.name_entry = ctk.CTkEntry(name_frame)
        self.name_entry.grid(row=0, column=1, padx=20, pady=20, sticky="we")

        timespan_frame = ctk.CTkFrame(self)
        timespan_frame.grid(row=current_row, column=0, sticky="we")
        current_row += 1
        timespan_label = ctk.CTkLabel(timespan_frame, text="Zeitslot:", font=ctk.CTkFont(size=16))
        timespan_label.grid(row=0, column=0, padx=20, pady=20, sticky="w")
        self.timespan_day_option = ctk.CTkOptionMenu(timespan_frame, values=WEEKDAYS)
        self.timespan_day_option.grid(row=0, column=1, padx=10)
        self.timespan_from_hour_option = ctk.CTkOptionMenu(
            timespan_frame, width=50, values=[f"{h:02d}:{15 * m:02d}" for h in range(8, 18) for m in range(4)]
        )
        self.timespan_from_hour_option.grid(row=0, column=2, padx=10)
        ctk.CTkLabel(timespan_frame, text="bis", font=ctk.CTkFont(size=16)).grid(row=0, column=3)
        self.timespan_to_hour_option = ctk.CTkOptionMenu(
            timespan_frame, width=50, values=[f"{h:02d}:{15 * m:02d}" for h in range(8, 18) for m in range(4)]
        )
        self.timespan_to_hour_option.grid(row=0, column=4, padx=10)

        first_date_frame = ctk.CTkFrame(self)
        first_date_frame.grid(row=current_row, column=0, sticky="we")
        current_row += 1
        first_date_label = ctk.CTkLabel(first_date_frame, text="Erster Termin:", font=ctk.CTkFont(size=16))
        first_date_label.grid(row=0, column=0, padx=20, pady=20, sticky="w")
        self.first_date_entry = ctk.CTkEntry(first_date_frame)
        self.first_date_entry.grid(row=0, column=1, padx=20, pady=20, sticky="we")

        capacity_frame = ctk.CTkFrame(self)
        capacity_frame.grid_columnconfigure(0, weight=1)
        capacity_frame.grid(row=current_row, column=0, sticky="we")
        current_row += 1
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
        self.max_capacity_label.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="w")
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
        max_capacity_slider.grid(row=2, column=1, padx=20, pady=(0, 20))

        self.update_capacity_labels()

        valid_grades_frame = ctk.CTkFrame(self)
        valid_grades_frame.grid_columnconfigure(0, weight=1)
        valid_grades_frame.grid(row=current_row, column=0, sticky="we")
        current_row += 1
        valid_grades_label = ctk.CTkLabel(valid_grades_frame, text="Klassen:", font=ctk.CTkFont(size=16))
        valid_grades_label.grid(row=0, column=0, columnspan=4, padx=20, pady=20, sticky="w")
        self.valid_grades_check_vars: list[ctk.BooleanVar] = []
        for grade in range(1, 5):
            check_var = ctk.BooleanVar(value=True)
            grade_checkbox = ctk.CTkCheckBox(
                valid_grades_frame, text=str(grade), variable=check_var, onvalue=True, offvalue=False
            )
            grade_checkbox.grid(row=1, column=grade - 1, padx=20, pady=10)
            self.valid_grades_check_vars.append(check_var)

        button_frame = ctk.CTkFrame(self)
        button_frame.grid(row=current_row, column=0, sticky="we")
        current_row += 1
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
        from_day, from_hour, from_minute = activity.timespan.get_from_day_hour_minute()
        to_day, to_hour, to_minute = activity.timespan.get_to_day_hour_minute()
        assert from_day == to_day
        self.timespan_day_option.set(WEEKDAYS[from_day])
        self.timespan_from_hour_option.set(f"{from_hour:02d}:{from_minute:02d}")
        self.timespan_to_hour_option.set(f"{to_hour:02d}:{to_minute:02d}")
        self.first_date_entry.insert(0, activity.first_date)
        self.min_capacity_var.set(activity.min_capacity)
        self.max_capacity_var.set(activity.max_capacity)
        for check_var, valid in zip(self.valid_grades_check_vars, activity.valid_grades):
            check_var.set(valid)
        self.update_capacity_labels()

    def on_accept(self):
        state = State()
        name = self.name_entry.get()
        day = WEEKDAYS.index(self.timespan_day_option.get())
        from_hour, from_minute = map(int, self.timespan_from_hour_option.get().split(":"))
        to_hour, to_minute = map(int, self.timespan_to_hour_option.get().split(":"))
        first_date = self.first_date_entry.get()
        min_capacity = self.min_capacity_var.get()
        max_capacity = self.max_capacity_var.get()
        valid_grades = [check_var.get() for check_var in self.valid_grades_check_vars]

        if min_capacity > max_capacity:
            open_error_popup(self, "Min. Teilnehmerzahl muss kleiner sein als max. Teilnehmerzahl!")
            return

        try:
            timespan = Timespan.from_day_hour_minute(day, from_hour, from_minute, day, to_hour, to_minute)
        except ValueError as e:
            open_error_popup(self, str(e))
            return

        if self.current_activity is not None:
            excluded_students = 0
            for student in state.students:
                if (
                    self.current_activity.id in student.preferences
                    and self.current_activity.is_valid_grade(student.grade)
                    and not valid_grades[student.grade - 1]
                ):
                    excluded_students += 1
            if excluded_students > 0 and not confirm_choice(
                self,
                f"Aktivität wurde von {excluded_students} Kindern gewählt, die nach Reduktion "
                "erlaubter Klassen nun nicht mehr hier zugeteilt werden können.",
            ):
                return

            self.current_activity.name = name
            self.current_activity.timespan = timespan
            self.current_activity.first_date = first_date
            self.current_activity.min_capacity = min_capacity
            self.current_activity.max_capacity = max_capacity
            self.current_activity.valid_grades = valid_grades
        else:
            state.add_activity(
                Activity(
                    name=name,
                    min_capacity=min_capacity,
                    max_capacity=max_capacity,
                    timespan=timespan,
                    first_date=first_date,
                    valid_grades=valid_grades,
                )
            )
        self.destroy()
