from __future__ import annotations
from pathlib import Path
from typing import Any

from singleton_decorator import singleton
from activity import Activity, ActivityIDGenerator
from assignment import Assignment
from student import Student, StudentIDGenerator

from dataclasses import asdict

import json


@singleton
class State:
    students: list[Student]
    activities: list[Activity]
    assignment: Assignment

    def __init__(
        self,
    ) -> None:
        self.reset()

    def reset(self) -> None:
        self.set_students([])
        self.set_activities([])
        self.set_assignment(Assignment())

    def as_dict(self) -> dict[str, Any]:
        return {
            "students": [asdict(student) for student in self.students],
            "activities": [asdict(activity) for activity in self.activities],
            "assignment": self.assignment.as_dict(),
        }

    def set_students(self, students: list[Student]) -> State:
        self.students = students
        StudentIDGenerator().reset(max([student.id for student in self.students] or [0]) + 1)
        return self

    def set_activities(self, activities: list[Activity]) -> State:
        self.activities = activities
        ActivityIDGenerator().reset(max([activity.id for activity in self.activities] or [0]) + 1)
        return self

    def set_assignment(self, assignment: Assignment) -> State:
        self.assignment = assignment
        return self

    def from_dict(self, state_dict: dict[str, Any]) -> State:
        assert set(state_dict.keys()) == {"students", "activities", "assignment"}
        self.set_students([Student.from_dict(student) for student in state_dict["students"]])
        self.set_activities([Activity.from_dict(activity) for activity in state_dict["activities"]])
        self.set_assignment(Assignment.from_dict(state_dict["assignment"]))

        return self

    def write(self, file_path: Path) -> None:
        with open(file_path, "w") as f:
            f.write(json.dumps(self.as_dict(), ensure_ascii=False, indent=4))

    def read(self, file_path: Path) -> State:
        with open(file_path, "r") as f:
            state_dict = json.loads(f.read())
            return self.from_dict(state_dict)
