from __future__ import annotations
from pathlib import Path
from typing import Any

from singleton_decorator import singleton
from activity import Activity, ActivityIDGenerator
from assignment import Assignment
from id_generator import ID
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
        self.reset_assignment()

    def reset_student_id(self):
        StudentIDGenerator().reset(max([student.id for student in self.students] or [0]) + 1)

    def reset_activity_id(self):
        ActivityIDGenerator().reset(max([activity.id for activity in self.activities] or [0]) + 1)

    def as_dict(self) -> dict[str, Any]:
        return {
            "students": [asdict(student) for student in self.students],
            "activities": [asdict(activity) for activity in self.activities],
            "assignment": self.assignment.as_dict(),
        }

    def set_students(self, students: list[Student]) -> State:
        self.students = students
        self.reset_student_id()
        return self

    def add_student(self, student: Student) -> State:
        self.students.append(student)
        self.reset_student_id()
        return self

    def remove_student_by_id(self, student_id: ID) -> State:
        for i, student in enumerate(self.students):
            if student.id == student_id:
                self.students.pop(i)
                break
        self.reset_student_id()
        return self

    def set_activities(self, activities: list[Activity]) -> State:
        self.activities = activities
        self.reset_activity_id()
        self.reset_assignment()
        return self

    def add_activity(self, activity: Activity) -> State:
        self.activities.append(activity)
        self.reset_activity_id()
        self.reset_assignment()
        return self

    def remove_activity_by_id(self, activity_id: ID) -> State:
        for i, activity in enumerate(self.activities):
            if activity.id == activity_id:
                self.activities.pop(i)
                break

        for student in self.students:
            try:
                student.preferences.remove(activity_id)
            except ValueError:
                pass

        self.reset_activity_id()
        self.reset_assignment()
        return self

    def set_assignment(self, assignment: Assignment) -> State:
        self.assignment = assignment
        return self

    def reset_assignment(self) -> State:
        return self.set_assignment(Assignment())

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
