from tkinter import ttk
from typing import Any

import customtkinter as ctk
import numpy as np

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from abc import ABC, abstractmethod

from assignment import StudentIDNotAssigned
from state import State


class StateStatistic(ABC):
    @abstractmethod
    def display_stats(self):
        ...


class PreferenceCountsByCourse(ctk.CTkFrame, StateStatistic):
    def __init__(self, master: Any) -> None:
        ctk.CTkFrame.__init__(self, master)

        self.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(self, text="Anzahl Wahlen pro Kurs", font=ctk.CTkFont(weight="bold", size=20))
        title.grid(row=0, column=0, padx=20, pady=(20, 0), sticky="w")

        fig = Figure(figsize=(14, 6), dpi=100)
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
        pref_counts = {activity.id: [0] * 4 for activity in state.activities}

        for student in state.students:
            for preference in student.preferences:
                pref_counts[preference][student.grade - 1] += 1

        def shorten_str(s: str, maxlen: int) -> str:
            if len(s) <= maxlen:
                return s
            return f"{s[:maxlen-3]}..."

        data = {shorten_str(activity_names[key], 20): pref_counts[key] for key in activity_names}

        n_bars = len(data)

        n_segments_per_bar = len(next(iter(data.values())))

        indices = np.arange(n_bars)
        colors = ["dodgerblue", "deepskyblue", "turquoise", "mediumseagreen"]
        bars = []

        bottoms = np.zeros(n_bars)
        for i in range(n_segments_per_bar):
            y_vals = [data[key][i] for key in data]
            bars.extend(
                self.plot.bar(indices, y_vals, width=0.6, color=colors[i], label=f"Klasse {i+1}", bottom=bottoms)
            )
            bottoms += np.array(y_vals)

        self.plot.set_xticks(indices)
        self.plot.set_xticklabels(data.keys())
        self.plot.set_xlabel("Kurs")

        for bar in bars:
            self.plot.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_y() + bar.get_height() / 2,
                str(int(bar.get_height())) if bar.get_height() > 0 else "",
                va="center",
                ha="center",
            )

        for tick in self.plot.get_xticklabels():
            tick.set_rotation(45)
            tick.set_ha("right")

        self.plot.legend()

        self.canvas.draw()


class AssignmentCountsByCourse(ctk.CTkFrame, StateStatistic):
    def __init__(self, master: Any) -> None:
        ctk.CTkFrame.__init__(self, master)

        self.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(self, text="Anzahl Zuteilungen pro Kurs", font=ctk.CTkFont(weight="bold", size=20))
        title.grid(row=0, column=0, padx=20, pady=(20, 0), sticky="w")

        fig = Figure(figsize=(14, 6), dpi=100)
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

        data = {}
        student_id_map = {student.id: student for student in state.students}

        def shorten_str(s: str, maxlen: int) -> str:
            if len(s) <= maxlen:
                return s
            return f"{s[:maxlen-3]}..."

        for activity in state.activities:
            if not state.assignment.activity_known(activity.id):
                continue
            short_name = shorten_str(activity.name, 20)
            data[short_name] = ([0] * 4, activity.min_capacity, activity.max_capacity)
            for student_id in state.assignment.get_students_for_activity(activity.id):
                student = student_id_map[student_id]
                data[short_name][0][student.grade - 1] += 1

        n_bars = len(data)

        n_segments_per_bar = 4

        indices = np.arange(n_bars)
        colors = ["dodgerblue", "deepskyblue", "turquoise", "mediumseagreen"]
        bars = []

        bottoms = np.zeros(n_bars)
        for i in range(n_segments_per_bar):
            y_vals = [data[key][0][i] for key in data]
            bars.extend(
                self.plot.bar(indices, y_vals, width=0.6, color=colors[i], label=f"Klasse {i+1}", bottom=bottoms)
            )
            bottoms += np.array(y_vals)

        for idx, (_, min_capacity, max_capacity) in enumerate(data.values()):
            self.plot.hlines(
                min_capacity,
                indices[idx] - 0.25,
                indices[idx] + 0.25,
                colors="orange",
                label="Min. Kapazität" if idx == 0 else "",
            )
            self.plot.hlines(
                max_capacity,
                indices[idx] - 0.25,
                indices[idx] + 0.25,
                colors="red",
                label="Max. Kapazität" if idx == 0 else "",
            )

        self.plot.set_xticks(indices)
        self.plot.set_xticklabels(data.keys())
        self.plot.set_xlabel("Kurs")

        for bar in bars:
            self.plot.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_y() + bar.get_height() / 2,
                str(int(bar.get_height())) if bar.get_height() > 0 else "",
                va="center",
                ha="center",
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
        self.plot = fig.add_subplot(1, 1, 1)

        self.canvas = FigureCanvasTkAgg(fig, master=self)
        self.canvas.get_tk_widget().grid(row=1, column=0, padx=10, pady=10)

        self.display_stats()

    def display_stats(self):
        self.plot.clear()

        state = State()

        if state.assignment.is_empty():
            return

        count_counts = {count: 0 for count in range(5)}

        for student in state.students:
            try:
                assigned_courses_count = len(state.assignment.get_activities_for_student(student.id))
            except StudentIDNotAssigned:
                assigned_courses_count = 0
            if assigned_courses_count not in count_counts:
                count_counts[assigned_courses_count] = 0
            count_counts[assigned_courses_count] += 1

        colors = ["red", "dodgerblue", "deepskyblue", "turquoise", "mediumseagreen"]
        colors = [color for idx, color in enumerate(colors) if count_counts[idx] > 0]
        count_counts = {key: val for key, val in count_counts.items() if val > 0}

        labels = [f"{key} Kurse" for key in count_counts]
        counts = list(count_counts.values())

        _, _, autotexts = self.plot.pie(
            counts,
            labels=labels,
            autopct=lambda pct: f"{int(round(pct/100. * sum(counts))):d}\n({pct:.1f}%)",
            colors=colors,
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
            AssignmentCountsByCourse(statistics_view),
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
