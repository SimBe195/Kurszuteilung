from pathlib import Path

import customtkinter as ctk
import tkinter as tk
import tkinter.filedialog

from state import State
from .assignment_page import AssignmentPage
from .confirmation import confirm_choice
from .sidebar import Sidebar
from .statistics_page import StatisticsPage
from .students_page import StudentsPage
from .activity_page import ActivityPage
import pdf


class MainWindow(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Kurszuteilung")

        self.geometry("1280x720")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.main_frame = ctk.CTkFrame(master=self, corner_radius=0)
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid(row=0, column=1, sticky="nsew")

        self.activity_page = ActivityPage(self.main_frame)
        self.activity_page.place(relx=0.0, rely=0.0, relwidth=1.0, relheight=1.0)
        self.student_page = StudentsPage(self.main_frame)
        self.student_page.place(relx=0.0, rely=0.0, relwidth=1.0, relheight=1.0)
        self.assignment_page = AssignmentPage(self.main_frame)
        self.assignment_page.place(relx=0.0, rely=0.0, relwidth=1.0, relheight=1.0)
        self.statistics_page = StatisticsPage(self.main_frame)
        self.statistics_page.place(relx=0.0, rely=0.0, relwidth=1.0, relheight=1.0)

        self.sidebar = Sidebar(self)

        self.sidebar.add_option(text="Kurse", page=self.activity_page)
        self.sidebar.add_option(text="Kinder", page=self.student_page)
        self.sidebar.add_option(text="Zuteilung", page=self.assignment_page)
        self.sidebar.add_option(text="Statistiken", page=self.statistics_page)
        self.sidebar.grid(row=0, column=0, sticky="nsw")
        self.sidebar.show_frame()

        self.add_menubar()

        self.last_save: Path | None = None

    def add_menubar(self) -> None:
        menu_bar = tk.Menu(self, tearoff=False)
        self.config(menu=menu_bar)

        file_menu = tk.Menu(menu_bar, tearoff=False)
        menu_bar.add_cascade(label="Datei", menu=file_menu)

        file_menu.add_command(label="Neu", accelerator="Strg+N", command=self.new)
        file_menu.add_command(label="Öffnen...", accelerator="Strg+O", command=self.load)
        file_menu.add_separator()
        file_menu.add_command(label="Speichern", accelerator="Strg+S", command=self.save)
        file_menu.add_command(label="Speichern Unter...", command=self.save_as)
        file_menu.add_separator()
        file_menu.add_command(label="Ansicht aktualisieren", command=self.update_display)
        file_menu.add_separator()
        file_menu.add_command(label="Beenden", accelerator="Strg+W", command=self.destroy)

        self.bind_all("<Control-n>", lambda _: self.new())
        self.bind_all("<Control-o>", lambda _: self.load())
        self.bind_all("<Control-s>", lambda _: self.save())
        self.bind_all("<Control-w>", lambda _: self.destroy())

        student_menu = tk.Menu(menu_bar, tearoff=False)
        menu_bar.add_cascade(label="Kinder", menu=student_menu)

        student_menu.add_command(label="Kind hinzufügen...", command=self.student_page.add_student)
        student_menu.add_command(label="Kind bearbeiten...", command=self.student_page.edit_student)
        student_menu.add_command(label="Kind entfernen...", command=self.student_page.remove_student)
        student_menu.add_separator()
        student_menu.add_command(label="Präferenzen löschen", command=self.student_page.reset_preferences)

        activity_menu = tk.Menu(menu_bar, tearoff=False)
        menu_bar.add_cascade(label="Kurse", menu=activity_menu)

        activity_menu.add_command(label="Kurs hinzufügen...", command=self.activity_page.add_activity)
        activity_menu.add_command(label="Kurs bearbeiten...", command=self.activity_page.edit_activity)
        activity_menu.add_command(label="Kurs entfernen...", command=self.activity_page.remove_activity)
        activity_menu.add_command(label="Kurs aufteilen...", command=self.activity_page.split_activity)

        assignment_menu = tk.Menu(menu_bar, tearoff=False)
        menu_bar.add_cascade(label="Zuteilung", menu=assignment_menu)

        assignment_menu.add_command(label="Zuteilung generieren", command=self.assignment_page.generate_assignment)
        assignment_menu.add_command(label="Zuteilung löschen", command=self.assignment_page.reset)

        export_menu = tk.Menu(menu_bar, tearoff=False)
        menu_bar.add_cascade(label="Export", menu=export_menu)

        export_menu.add_command(label="Schülerzuteilungen...", command=self.export_per_student)
        export_menu.add_command(label="Schülerpräferenzen...", command=self.export_per_preference)
        export_menu.add_command(label="Kurszuteilungen...", command=self.export_per_activity)
        export_menu.add_command(label="Anwesenheitslisten...", command=self.export_attendance)

    def update_display(self):
        self.student_page.display_students()
        self.activity_page.display_activities()
        self.assignment_page.display_assignment()
        self.statistics_page.display_statistics()

    def new(self):
        if not confirm_choice(
            self, "Es sind möglicherweise nicht-gespeicherte Änderungen vorhanden. Wirklich fortfahren?"
        ):
            return

        self.last_save = None
        State().reset()
        self.update_display()

    def load(self):
        result = tk.filedialog.askopenfilename(parent=self, filetypes=[("json", "*.json")])
        if not result:
            return
        result_path = Path(result)
        if not result_path.is_file():
            return
        self.last_save = result_path
        State().read(self.last_save)
        self.update_display()

    def save(self):
        if self.last_save is not None:
            State().write(self.last_save)
        else:
            self.save_as()

    def save_as(self):
        result = tk.filedialog.asksaveasfilename(parent=self, defaultextension=".json", filetypes=[("json", "*.json")])
        if not result:
            return
        result_path = Path(result)
        self.last_save = result_path
        self.save()

    def export_per_student(self):
        result = tk.filedialog.asksaveasfilename(parent=self, defaultextension=".pdf", filetypes=[("pdf", "*.pdf")])
        if not result:
            return
        result_path = Path(result)
        state = State()
        pdf.create_student_assignment_pdf(state.students, state.activities, state.assignment, result_path)

    def export_per_activity(self):
        result = tk.filedialog.asksaveasfilename(parent=self, defaultextension=".pdf", filetypes=[("pdf", "*.pdf")])
        if not result:
            return
        result_path = Path(result)
        state = State()
        pdf.create_course_assignment_pdf(state.students, state.activities, state.assignment, result_path)

    def export_per_preference(self):
        result = tk.filedialog.asksaveasfilename(parent=self, defaultextension=".pdf", filetypes=[("pdf", "*.pdf")])
        if not result:
            return
        result_path = Path(result)
        state = State()
        pdf.create_course_preference_pdf(state.students, state.activities, state.assignment, result_path)

    def export_attendance(self):
        result = tk.filedialog.asksaveasfilename(parent=self, defaultextension=".pdf", filetypes=[("pdf", "*.pdf")])
        if not result:
            return
        result_path = Path(result)
        state = State()
        pdf.create_course_attendance_list_pdf(state.students, state.activities, state.assignment, result_path)
