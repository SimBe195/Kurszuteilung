from functools import partial
from typing import Any, Generic, TypeVar, Callable

import customtkinter as ctk

from activity import Activity
from state import State
from student import Student

ResultType = TypeVar("ResultType")


class SearchDialog(ctk.CTkToplevel, Generic[ResultType]):
    def __init__(
        self,
        master: Any,
        title: str,
        search_space: dict[str, ResultType],
        columns: list[tuple[str, Callable[[ResultType], str]]],
    ):
        ctk.CTkToplevel.__init__(self, master)

        self.title(title)

        self.grid_columnconfigure(0, weight=1)

        self.search_entry = ctk.CTkEntry(self, placeholder_text="Suchbegriff eingeben...")
        self.search_entry.grid(row=0, column=0, padx=(20, 0), pady=30, sticky="we")
        self.search_entry.bind("<Return>", command=lambda _: self.search())

        search_button = ctk.CTkButton(self, text="Suchen", command=self.search)
        search_button.grid(row=0, column=1, padx=(10, 20), pady=30)

        self.results_frame = ctk.CTkScrollableFrame(self, width=550)
        self.results_frame.grid(row=1, column=0, columnspan=2, padx=20, pady=20, sticky="nsew")

        close_button = ctk.CTkButton(self, text="Schließen", command=self.destroy)
        close_button.grid(row=2, column=0, columnspan=2, padx=20, pady=20)

        self.search_space = search_space
        self.columns = columns

        self.result: ResultType | None = None

        self.search()

    def search(self):
        for widget in self.results_frame.winfo_children():
            widget.destroy()

        search_term = self.search_entry.get().lower()
        if search_term:
            results = [value for key, value in self.search_space.items() if search_term in key]
        else:
            results = list(self.search_space.values())

        if len(results) == 0:
            result_label = ctk.CTkLabel(self.results_frame, text="Keine Ergebnisse")
            result_label.grid(row=0, column=0)
            return

        for idx, (title, _) in enumerate(self.columns):
            column_title = ctk.CTkLabel(self.results_frame, text=title, font=ctk.CTkFont(size=14))
            column_title.grid(row=0, column=idx, padx=20)

        for row, result in enumerate(results, start=1):
            for column, (_, attribute_getter) in enumerate(self.columns):
                column_label = ctk.CTkLabel(
                    self.results_frame, text=attribute_getter(result), width=30, font=ctk.CTkFont(size=12)
                )
                column_label.grid(row=row, column=column, pady=5)

            accept_button = ctk.CTkButton(
                self.results_frame,
                text="Auswählen",
                font=ctk.CTkFont(size=12),
                command=partial(self.finish, result=result),
            )
            accept_button.grid(row=row, column=3, pady=5, padx=10)

    def finish(self, result: ResultType):
        self.result = result
        self.destroy()


def search_student(master: Any) -> Student | None:
    dialog = SearchDialog(
        master,
        title="Kind auswählen",
        search_space={
            f"{student.id} {student.name} {student.grade}{student.subgrade}".lower(): student
            for student in State().students
        },
        columns=[
            ("ID", lambda student: student.id),
            ("Name", lambda student: student.name),
            ("Klasse", lambda student: str(student.grade) + student.subgrade),
        ],
    )
    dialog.after(50, lambda: dialog.focus_set())
    master.wait_window(dialog)
    return dialog.result


def search_activity(master: Any) -> Activity | None:
    dialog = SearchDialog(
        master,
        title="Kurs auswählen",
        search_space={f"{activity.id} {activity.name}".lower(): activity for activity in State().activities},
        columns=[
            ("ID", lambda activity: activity.id),
            ("Bezeichnung", lambda activity: activity.name),
        ],
    )
    dialog.after(50, lambda: dialog.focus_set())
    master.wait_window(dialog)
    return dialog.result
