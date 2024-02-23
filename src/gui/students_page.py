from tkinter import ttk
from typing import Any

import customtkinter as ctk

from activity import get_activity_id_map
from gui.confirmation import confirm_choice
from gui.search_dialog import search_student
from id_generator import ID
from state import State
from student import Student


class StudentsPage(ctk.CTkFrame):
    def __init__(self, master: Any) -> None:
        ctk.CTkFrame.__init__(self, master)

        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(self, text="Kinder", font=ctk.CTkFont(size=32))
        title.grid(row=0, column=0, padx=20, pady=(20, 0), sticky="w")

        separator = ttk.Separator(self, orient="horizontal")
        separator.grid(row=1, column=0, padx=10, pady=20, sticky="ew")

        button_frame = ctk.CTkFrame(self, fg_color=self.cget("fg_color"))
        button_frame.grid(row=2, column=0, padx=20, sticky="w")
        add_student_button = ctk.CTkButton(
            button_frame, text="Hinzufügen", font=ctk.CTkFont(size=18), command=self.add_student
        )
        add_student_button.grid(row=0, column=0, padx=10)

        edit_student_button = ctk.CTkButton(
            button_frame, text="Bearbeiten", font=ctk.CTkFont(size=18), command=self.edit_student
        )
        edit_student_button.grid(row=0, column=1, padx=10)

        remove_student_button = ctk.CTkButton(
            button_frame, text="Entfernen", font=ctk.CTkFont(size=18), command=self.remove_student
        )
        remove_student_button.grid(row=0, column=2, padx=10)

        reset_preferences_button = ctk.CTkButton(
            button_frame, text="Präferenzen löschen", font=ctk.CTkFont(size=18), command=self.reset_preferences
        )
        reset_preferences_button.grid(row=0, column=3, padx=10, sticky="e")

        self.student_view = ctk.CTkScrollableFrame(self)
        self.student_view.grid(row=3, column=0, padx=20, pady=30, sticky="nsew")

        for idx, title in enumerate(["ID", "Name", "Klasse", "Präferenzen"]):
            column_title = ctk.CTkLabel(self.student_view, text=title, font=ctk.CTkFont(size=20))
            column_title.grid(row=0, column=idx, padx=20)

        self.display_students()

    def add_student(self):
        dialog = ModifyStudentDialog(self, title="Kind hinzufügen")
        dialog.after(50, lambda: dialog.focus_set())
        self.wait_window(dialog)
        self.display_students()

    def edit_student(self):
        if (student := search_student(self)) is None:
            return
        dialog = ModifyStudentDialog(self, title="Kind bearbeiten")
        dialog.insert_student_data(student)
        dialog.after(50, lambda: dialog.focus_set())
        self.wait_window(dialog)
        self.display_students()

    def remove_student(self):
        if (student := search_student(self)) is not None:
            if confirm_choice(self, f'Kind "{student.name}" ({student.grade}{student.subgrade}) wirklich entfernen?'):
                State().remove_student_by_id(student.id)
                self.display_students()

    def reset_preferences(self):
        if confirm_choice(self, f"Wirklich alle eingetragenen Präferenzen löschen?"):
            for student in State().students:
                student.preferences = []
                State().reset_assignment()
            self.display_students()

    def display_students(self):
        for widget in self.student_view.winfo_children():
            if widget.grid_info()["row"] > 0:
                widget.destroy()

        state = State()
        activity_id_map = get_activity_id_map(state.activities)
        for row, student in enumerate(state.students, start=1):
            id_label = ctk.CTkLabel(self.student_view, text=str(student.id), font=ctk.CTkFont(size=16))
            id_label.grid(row=row, column=0, pady=5, sticky="nsew")

            name_label = ctk.CTkLabel(self.student_view, text=student.name, font=ctk.CTkFont(size=16))
            name_label.grid(row=row, column=1, pady=5, sticky="nsew")

            grade_label = ctk.CTkLabel(
                self.student_view, text=str(student.grade) + student.subgrade, font=ctk.CTkFont(size=16)
            )
            grade_label.grid(row=row, column=2, pady=5, sticky="nsew")

            preference_text = ", ".join([activity_id_map[activity_id].name for activity_id in student.preferences])
            preference_label = ctk.CTkLabel(self.student_view, text=preference_text, font=ctk.CTkFont(size=16))
            preference_label.grid(row=row, column=3, pady=5, sticky="nsew")


class ModifyStudentDialog(ctk.CTkToplevel):
    def __init__(self, master: Any, title: str) -> None:
        ctk.CTkToplevel.__init__(self, master)

        self.title(title)

        self.grid_columnconfigure(0, weight=1)

        name_frame = ctk.CTkFrame(self)
        name_frame.grid_columnconfigure(1, weight=1)
        name_frame.grid(row=0, column=0, sticky="we")
        name_label = ctk.CTkLabel(name_frame, text="Name:", font=ctk.CTkFont(size=16))
        name_label.grid(row=0, column=0, padx=20, pady=20, sticky="w")
        self.name_entry = ctk.CTkEntry(name_frame)
        self.name_entry.grid(row=0, column=1, padx=20, pady=20, sticky="we")

        grade_frame = ctk.CTkFrame(self)
        grade_frame.grid(row=1, column=0, sticky="we")
        grade_label = ctk.CTkLabel(grade_frame, text="Klasse:", font=ctk.CTkFont(size=16))
        grade_label.grid(row=0, column=0, padx=20, pady=20, sticky="w")
        self.grade_option = ctk.CTkOptionMenu(
            grade_frame,
            values=[grade + subgrade for grade in ["1", "2", "3", "4"] for subgrade in ["a", "b", "c", "d"]],
        )

        self.grade_option.grid(row=0, column=1, padx=20, pady=20)

        preference_frame = ctk.CTkScrollableFrame(self)
        preference_frame.grid_columnconfigure(0, weight=1)
        preference_frame.grid_columnconfigure(1, weight=1)
        preference_frame.grid(row=2, column=0, sticky="we")
        preference_label = ctk.CTkLabel(preference_frame, text="Präferenzen:", font=ctk.CTkFont(size=16))
        preference_label.grid(row=0, column=0, columnspan=2, padx=20, pady=20, sticky="w")
        self.preference_check_vars: dict[ID, ctk.BooleanVar] = {}
        self.preference_check_vars_2: dict[ID, ctk.BooleanVar] = {}
        for activity_idx, activity in enumerate(State().activities, start=0):
            check_var = ctk.BooleanVar(value=False)
            activity_checkbox = ctk.CTkCheckBox(
                preference_frame, text="", variable=check_var, onvalue=True, offvalue=False
            )
            activity_checkbox.grid(row=1 + activity_idx, column=0, padx=(20, 0), pady=1, sticky="e")
            self.preference_check_vars[activity.id] = check_var

            check_var_2 = ctk.BooleanVar(value=False)
            activity_checkbox_2 = ctk.CTkCheckBox(
                preference_frame, text=activity.name, variable=check_var_2, onvalue=True, offvalue=False
            )
            activity_checkbox_2.grid(row=1 + activity_idx, column=1, padx=(0, 20), pady=1, sticky="w")
            self.preference_check_vars_2[activity.id] = check_var_2

        button_frame = ctk.CTkFrame(self)
        button_frame.grid(row=3, column=0, sticky="we")
        accept_button = ctk.CTkButton(button_frame, text="Akzeptieren", command=self.on_accept)
        accept_button.grid(row=0, column=0, padx=20, pady=20)

        cancel_button = ctk.CTkButton(button_frame, text="Abbrechen", command=self.destroy)
        cancel_button.grid(row=0, column=1, padx=20, pady=20)

        self.current_student: Student | None = None

    def insert_student_data(self, student: Student):
        self.current_student = student
        self.name_entry.insert(0, student.name)
        self.grade_option.set(str(student.grade) + student.subgrade)
        for activity_id in student.preferences:
            if self.preference_check_vars[activity_id].get():
                self.preference_check_vars_2[activity_id].set(True)
            else:
                self.preference_check_vars[activity_id].set(True)

    def on_accept(self):
        state = State()
        name = self.name_entry.get()
        grade = int(self.grade_option.get()[0])
        subgrade = self.grade_option.get()[1]
        preferences = [activity_id for activity_id, check_var in self.preference_check_vars.items() if check_var.get()]
        preferences += [
            activity_id for activity_id, check_var in self.preference_check_vars_2.items() if check_var.get()
        ]

        activity_map = get_activity_id_map(state.activities)
        for activity_id in preferences:
            if not activity_map[activity_id].is_valid_grade(grade) and not confirm_choice(
                self,
                f"Präferenz für Aktivität {activity_map[activity_id].name} angegeben, "
                f"die keine Kinder aus Klasse {grade} zulässt.",
            ):
                return

        if self.current_student is not None:
            self.current_student.name = name
            self.current_student.grade = grade
            self.current_student.subgrade = subgrade
            self.current_student.preferences = preferences
        else:
            state.add_student(
                Student(
                    name=name,
                    grade=grade,
                    subgrade=subgrade,
                    preferences=preferences,
                )
            )
        self.destroy()
