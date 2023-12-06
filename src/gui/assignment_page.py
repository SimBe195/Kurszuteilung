import copy
from tkinter import ttk
from typing import Any

import customtkinter as ctk

from activity import Activity
from assignment import assign_students, Assignment
from gui.confirmation import confirm_choice
from state import State


class AssignmentPage(ctk.CTkFrame):
    def __init__(self, master: Any) -> None:
        ctk.CTkFrame.__init__(self, master)

        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(self, text="Zuteilung", font=ctk.CTkFont(size=32))
        title.grid(row=0, column=0, padx=20, pady=(20, 0), sticky="w")

        separator = ttk.Separator(self, orient="horizontal")
        separator.grid(row=1, column=0, padx=10, pady=20, sticky="ew")

        button_frame = ctk.CTkFrame(self, fg_color=self.cget("fg_color"))
        button_frame.grid(row=2, column=0, padx=20, sticky="w")

        generate_assignment_button = ctk.CTkButton(
            button_frame, text="Generieren", font=ctk.CTkFont(size=18), command=self.generate_assignment
        )
        generate_assignment_button.grid(row=0, column=0, padx=10)

        edit_assignment_button = ctk.CTkButton(
            button_frame, text="Löschen", font=ctk.CTkFont(size=18), command=self.reset
        )
        edit_assignment_button.grid(row=0, column=1, padx=10)

        self.assignment_view = ctk.CTkScrollableFrame(self)
        self.assignment_view.grid(row=3, column=0, padx=20, pady=30, sticky="nsew")
        self.assignment_view.grid_columnconfigure(0, weight=1)
        self.assignment_view.grid_columnconfigure(1, weight=1)

        self.display_assignment()

    def reset(self):
        if confirm_choice(self, "Zuteilung wirklich löschen?"):
            State().set_assignment(Assignment())
            self.display_assignment()

    def generate_assignment(self):
        state = State()
        new_assignment = assign_students(state.students, state.activities)

        exceptions = new_assignment.check_validity(state.students, state.activities)

        if len(exceptions) > 0:
            confirmation_text = f"Zuteilung enthält {len(exceptions)} Fehler:\n\n" + "\n\n".join(
                map(str, exceptions[:10])
            )
            if not confirm_choice(self, confirmation_text):
                return

        state.set_assignment(new_assignment)

        self.display_assignment()
        self.focus_set()

    def display_assignment(self):
        for widget in self.assignment_view.winfo_children():
            widget.destroy()
        state = State()
        student_id_map = {student.id: student for student in state.students}
        activities = copy.deepcopy(state.activities)
        activities.append(Activity(name="Kein Kurs", id=-1))

        for activity_idx, activity in enumerate(activities):
            activity_frame = ctk.CTkFrame(self.assignment_view)
            activity_frame.grid(row=activity_idx // 2, column=activity_idx % 2, padx=20, pady=20, sticky="nsew")

            activity_title = ctk.CTkLabel(activity_frame, text=activity.name, font=ctk.CTkFont(size=22))
            activity_title.grid(row=0, column=0, columnspan=3, padx=5, pady=20)

            if activity.id != -1:
                if not state.assignment.activity_known(activity.id):
                    continue
                student_ids = state.assignment.get_students_for_activity(activity.id)
            else:
                student_ids = [
                    student.id
                    for student in state.students
                    if not state.assignment.student_known(student.id)
                    or len(state.assignment.get_activities_for_student(student.id)) == 0
                ]

            for student_row, student_id in enumerate(student_ids, start=1):
                student = student_id_map[student_id]

                index_label = ctk.CTkLabel(activity_frame, text=f"{student_row}.", font=ctk.CTkFont(size=16))
                index_label.grid(row=student_row, column=0, padx=5)

                student_name_label = ctk.CTkLabel(activity_frame, text=student.name, font=ctk.CTkFont(size=16))
                student_name_label.grid(row=student_row, column=1, padx=20)

                student_grade_label = ctk.CTkLabel(
                    activity_frame, text=str(student.grade) + student.subgrade, font=ctk.CTkFont(size=16)
                )
                student_grade_label.grid(row=student_row, column=2, padx=20)
