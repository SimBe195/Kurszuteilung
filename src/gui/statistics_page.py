from tkinter import ttk
from typing import Any

import customtkinter as ctk
import numpy as np

from icecream import ic

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from abc import ABC, abstractmethod

from assignment import StudentIDNotAssigned
from state import State


class StateStatistic(ABC):
    @abstractmethod
    def display_stats(self):
        ...


"""
TODO: Statistics for
 - Anzahl Wahlen pro Kind (z. B. wie viele Kinder haben einen, zwei, etc. Kurse angegeben)
 - Anzahl Belegungen pro Kurs
    - + Unterteilung nach Jahrgangsstufe
     - Anzahl von Kindern mit 1/2/3/... Kursen
 - Kinder in Schnittmengen von Kursen (z. B. wer ist in Basteln und Filzen)
"""


class PreferenceCountsByCourse(ctk.CTkFrame, StateStatistic):
    def __init__(self, master: Any) -> None:
        ctk.CTkFrame.__init__(self, master)

        self.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(self, text="Anzahl Wahlen pro Kurs", font=ctk.CTkFont(weight="bold", size=20))
        title.grid(row=0, column=0, padx=20, pady=(20, 0), sticky="w")

        fig = Figure(figsize=(13, 6), dpi=100)
        fig.subplots_adjust(left=0.05, bottom=0.25)
        self.plot = fig.add_subplot(1, 1, 1)

        self.canvas = FigureCanvasTkAgg(fig, master=self)
        self.canvas.get_tk_widget().grid(row=1, column=0, padx=10, pady=10)

        self.display_stats()

    def display_stats(self):
        self.plot.clear()

        state = State()

        if len(state.activities) == 0:
            return

        activity_names = {activity.id: activity.name for activity in state.activities}
        pref_counts = {activity.id: [0] * 5 for activity in state.activities}

        for student in state.students:
            for preference in student.preferences:
                pref_counts[preference][student.grade - 1] += 1
                pref_counts[preference][-1] += 1

        def shorten_str(s: str, maxlen: int) -> str:
            if len(s) <= maxlen:
                return s
            return f"{s[:maxlen-3]}..."

        data = {shorten_str(activity_names[key], 20): pref_counts[key] for key in activity_names}

        n_groups = len(data)
        n_bars_per_group = len(next(iter(data.values())))

        indices = np.arange(n_groups)
        colors = ["m", "g", "r", "c", "b"]
        bar_width = 0.15
        bar_locs = [indices + (i - (n_bars_per_group - 1) / 2) * bar_width for i in range(n_bars_per_group)]

        bars = []
        for i in range(n_bars_per_group):
            y_vals = [data[key][i] for key in data]
            if i < 4:
                label = f"Klasse {i+1}"
            else:
                label = "Gesamt"
            bars.extend(self.plot.bar(bar_locs[i], y_vals, width=bar_width, color=colors[i % 5], label=label))

        self.plot.set_xticks(indices)
        self.plot.set_xticklabels(data.keys())
        self.plot.set_xlabel("Kurs")

        for bar in bars:
            self.plot.text(
                bar.get_x() + bar.get_width() / 2, bar.get_height(), str(bar.get_height()), va="bottom", ha="center"
            )

        for tick in self.plot.get_xticklabels():
            tick.set_rotation(45)
            tick.set_ha("right")

        self.plot.legend()

        self.canvas.draw()


class AssignmentCountCounts(ctk.CTkFrame, StateStatistic):
    def __init__(self, master: Any) -> None:
        ctk.CTkFrame.__init__(self, master)

        self.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            self, text="Anzahl Kinder mit zugewiesener Kurszahl", font=ctk.CTkFont(weight="bold", size=20)
        )
        title.grid(row=0, column=0, padx=20, pady=(20, 0), sticky="w")

        fig = Figure(figsize=(6, 6), dpi=100)
        fig.subplots_adjust(left=0.05, bottom=0.25)
        self.plot = fig.add_subplot(1, 1, 1)

        self.canvas = FigureCanvasTkAgg(fig, master=self)
        self.canvas.get_tk_widget().grid(row=1, column=0, padx=10, pady=10)

        self.display_stats()

    def display_stats(self):
        self.plot.clear()

        state = State()

        if state.assignment.is_empty():
            return

        count_counts = {count: 0 for count in range(10)}

        for student in state.students:
            try:
                assigned_courses_count = len(state.assignment.get_activities_for_student(student.id))
            except StudentIDNotAssigned:
                assigned_courses_count = 0
            if assigned_courses_count not in count_counts:
                count_counts[assigned_courses_count] = 0
            count_counts[assigned_courses_count] += 1

        count_counts = {key: val for key, val in count_counts.items() if val > 0}

        labels = [f"{key} Kurse" for key in count_counts]
        counts = list(count_counts.values())

        _, _, autotexts = self.plot.pie(
            counts,
            labels=labels,
            autopct=lambda pct: f"{int(round(pct/100. * sum(counts))):d}\n({pct:.1f}%)",
            textprops={"color": "w"},
        )

        for autotext in autotexts:
            autotext.set_color("black")

        self.plot.legend()

        self.canvas.draw()


class StatisticsPage(ctk.CTkFrame):
    def __init__(self, master: Any) -> None:
        ctk.CTkFrame.__init__(self, master)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        title = ctk.CTkLabel(self, text="Statistiken", font=ctk.CTkFont(size=32))
        title.grid(row=0, column=0, padx=20, pady=(20, 0), sticky="w")

        separator = ttk.Separator(self, orient="horizontal")
        separator.grid(row=1, column=0, padx=10, pady=20, sticky="ew")

        statistics_view = ctk.CTkScrollableFrame(self)
        statistics_view.grid(row=2, column=0, padx=10, pady=0, sticky="nsew")
        statistics_view.grid_columnconfigure(0, weight=1)

        self.statistic_frames = [
            PreferenceCountsByCourse(statistics_view),
            AssignmentCountCounts(statistics_view),
        ]
        for idx, frame in enumerate(self.statistic_frames):
            frame.grid(row=1 + 2 * idx, column=0, padx=10, pady=10, sticky="ew")
            separator = ttk.Separator(statistics_view, orient="horizontal")
            separator.grid(row=2 + 2 * idx, column=0, padx=10, pady=20, sticky="ew")

        self.display_statistics()

    def display_statistics(self):
        for frame in self.statistic_frames:
            frame.display_stats()
