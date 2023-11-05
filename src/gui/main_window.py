import customtkinter as ctk
import tkinter as tk

from .assignment_page import AssignmentPage
from .sidebar import Sidebar
from .students_page import StudentsPage
from .courses_page import CoursesPage


class MainWindow(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Kurszuteilung")

        self.geometry("1280x720")

        self.sidebar = Sidebar(self)

        self.main_frame = ctk.CTkFrame(master=self, corner_radius=0)
        self.main_frame.pack(side="right", expand=True, fill="both")

        course_page = CoursesPage(self.main_frame)
        course_page.place(relx=0.0, rely=0.0, relwidth=1.0, relheight=1.0)
        student_page = StudentsPage(self.main_frame)
        student_page.place(relx=0.0, rely=0.0, relwidth=1.0, relheight=1.0)
        assignment_page = AssignmentPage(self.main_frame)

        self.sidebar.add_option(text="Kurse", page=course_page)
        self.sidebar.add_option(text="Kinder", page=student_page)
        self.sidebar.add_option(text="Zuteilung", page=assignment_page)
        self.sidebar.pack()
        self.sidebar.show_frame()

    def add_menubar(self) -> None:
        menu_bar = tk.Menu(self, tearoff=False)
        self.config(menu=menu_bar)
        file_menu = tk.Menu(menu_bar, tearoff=False)
        menu_bar.add_cascade(label="Datei", menu=file_menu)

        file_menu.add_command(label="Neu")
        file_menu.add_command(label="Öffnen...")
        file_menu.add_separator()
        file_menu.add_command(label="Speichern")
        file_menu.add_command(label="Speichern Unter...")
        file_menu.add_separator()
        file_menu.add_command(label="Beenden", command=self.destroy)
