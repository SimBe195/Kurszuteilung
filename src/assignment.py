from __future__ import annotations

from collections import defaultdict
from typing import Any

from activity import Activity
from id_generator import ID
from student import Student


class AssignmentException(Exception):
    pass


class StudentIDDoesNotExist(AssignmentException):
    def __init__(self, student_id: ID):
        super().__init__(f"Versucht, Kind mit unbekannter ID {student_id} aus einem Kurs zu entfernen.")


class ActivityIDDoesNotExist(AssignmentException):
    def __init__(self, activity_id: ID):
        super().__init__(f"Versucht, ein Kind aus einem Kurs mit unbekannter ID {activity_id} zu entfernen.")


class NoAssignedActivity(AssignmentException):
    def __init__(self, student: Student):
        super().__init__(f"Kind {student} ist zu keinem Kurs zugeteilt.")


class NotAssignedToActivity(AssignmentException):
    def __init__(self, student_id: ID, activity_id: ID):
        super().__init__(f"Kind mit ID {student_id} ist nicht zum Kurs mit ID {activity_id} zugeteilt.")


class EmptyPreferences(AssignmentException):
    def __init__(self, student: Student):
        super().__init__(f"Kind {student} hat keine Präferenzen angegeben.")


class MinimumCapacityNotReached(AssignmentException):
    def __init__(self, activity: Activity, participant_count: int):
        super().__init__(f"Nur {participant_count} Kinder sind zum Kurs {activity} zugeteilt.")


class MaximumCapacityReached(AssignmentException):
    def __init__(self, activity: Activity, participant_count: int):
        super().__init__(f"{participant_count} Kinder sind zum Kurs {activity} zugeteilt.")


class GradeRestrictionViolation(AssignmentException):
    def __init__(self, student: Student, activity: Activity):
        super().__init__(f"Klasse von Kind {student} ist in Kurs {activity} nicht erlaubt.")


class ActivityNotPreferred(AssignmentException):
    def __init__(self, student: Student, activity: Activity):
        super().__init__(f"Kind {student} ist zu Kurs {activity} hinzugefügt den es nicht gewählt hat.")


class Assignment:
    def __init__(self):
        self._student_to_activities_map: defaultdict[ID, set[ID]] = defaultdict(set)
        self._activity_to_students_map: defaultdict[ID, set[ID]] = defaultdict(set)

    def as_dict(self) -> dict[str, Any]:
        return {
            "student_activity_map": {
                student_id: list(activity_ids) for student_id, activity_ids in self._student_to_activities_map.items()
            },
            "activity_student_map": {
                activity_id: list(student_ids) for activity_id, student_ids in self._activity_to_students_map.items()
            },
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Assignment:
        assert set(data.keys()) == {"student_activity_map", "activity_student_map"}
        assignment = cls()
        assignment._student_to_activities_map = {
            int(student_id): set(activity_ids) for student_id, activity_ids in data["student_activity_map"].items()
        }
        assignment._activity_to_students_map = {
            int(activity_id): set(student_ids) for activity_id, student_ids in data["activity_student_map"].items()
        }

        return assignment

    def __eq__(self, other: Assignment) -> bool:
        if not set(self._student_to_activities_map.keys()) == set(other._student_to_activities_map.keys()):
            return False
        if not set(self._activity_to_students_map.keys()) == set(other._activity_to_students_map.keys()):
            return False

        for student_id in self._student_to_activities_map:
            if not self._student_to_activities_map[student_id] == other._student_to_activities_map[student_id]:
                return False
        for activity_id in self._activity_to_students_map:
            if not self._activity_to_students_map[activity_id] == other._activity_to_students_map[activity_id]:
                return False
        return True

    def student_known(self, student_id: ID) -> bool:
        return student_id in self._student_to_activities_map

    def activity_known(self, activity_id: ID) -> bool:
        return activity_id in self._activity_to_students_map

    def get_activities_for_student(self, student_id: ID) -> list[ID]:
        if student_id not in self._student_to_activities_map:
            raise StudentIDDoesNotExist(student_id)

        return list(self._student_to_activities_map[student_id])

    def get_students_for_activity(self, activity_id: ID) -> list[ID]:
        if activity_id not in self._activity_to_students_map:
            raise ActivityIDDoesNotExist(activity_id)
        return list(self._activity_to_students_map[activity_id])

    def assign_student_to_activity_by_id(self, student_id: ID, activity_id: ID) -> None:
        self._student_to_activities_map[student_id].add(activity_id)
        self._activity_to_students_map[activity_id].add(student_id)

    def assign_student_to_activity(self, student: Student, activity: Activity) -> None:
        if not activity.is_valid_grade(student.grade):
            raise GradeRestrictionViolation(student, activity)
        self.assign_student_to_activity_by_id(student.id, activity.id)

    def remove_student_from_activity_by_id(self, student_id: ID, activity_id: ID) -> None:
        if student_id not in self._student_to_activities_map:
            raise StudentIDDoesNotExist(student_id)
        if activity_id not in self._student_to_activities_map[student_id]:
            raise NotAssignedToActivity(student_id, activity_id)

        self._student_to_activities_map[student_id].remove(activity_id)
        self._activity_to_students_map[activity_id].remove(student_id)

    def participant_count(self, activity_id: ID) -> int:
        if activity_id not in self._activity_to_students_map:
            raise ActivityIDDoesNotExist(activity_id)
        return len(self._activity_to_students_map[activity_id])

    def check_validity(self, students: list[Student], activities: list[Activity]) -> None:
        activity_map = {activity.id: activity for activity in activities}

        for student in students:
            assigned_activities = self.get_activities_for_student(student.id)
            if len(assigned_activities) == 0:
                raise NoAssignedActivity(student)

            for activity_id in assigned_activities:
                activity = activity_map[activity_id]
                if activity_id not in student.preferences:
                    raise ActivityNotPreferred(student, activity)

                if not activity.is_valid_grade(student.grade):
                    raise GradeRestrictionViolation(student, activity)

        for activity in activities:
            participant_count = self.participant_count(activity.id)
            if participant_count < activity.min_capacity:
                raise MinimumCapacityNotReached(activity, participant_count)
            if participant_count > activity.max_capacity:
                raise MaximumCapacityReached(activity, participant_count)


def reduce_overbooking(assignment: Assignment, activities: list[Activity]) -> None:
    # Find an overbooked activity that we can attempt to reduce
    for activity in activities:
        if assignment.participant_count(activity.id) <= activity.max_capacity:
            continue  # Skip if activity is not overbooked

        # Try to remove a student from the activity and recurse
        # Ger all students that have been assigned to the given activity

        valid_removal_found = False
        student_ids = assignment.get_students_for_activity(activity.id)
        for student_id in student_ids:
            # If the student is not assigned to any other activity, they can't be removed
            if len(assignment.get_activities_for_student(student_id)) <= 1:
                continue

            assignment.remove_student_from_activity_by_id(student_id, activity.id)

            try:
                reduce_overbooking(assignment, activities)
                valid_removal_found = True
            except MaximumCapacityReached:
                assignment.assign_student_to_activity_by_id(student_id, activity.id)

        if not valid_removal_found:
            raise MaximumCapacityReached(activity, assignment.participant_count(activity.id))


def assign_students(students: list[Student], activities: list[Activity]) -> Assignment:
    activity_map = {activity.id: activity for activity in activities}
    assignment = Assignment()

    # First, assign all students their preferred activities
    for student in students:
        if len(student.preferences) == 0:
            raise EmptyPreferences(student)
        for activity_id in student.preferences:
            if activity_id not in activity_map:
                raise ActivityIDDoesNotExist(activity_id)
            activity = activity_map[activity_id]
            assignment.assign_student_to_activity(student, activity)

    # Check min capacity
    for activity in activities:
        if (participants := assignment.participant_count(activity.id)) < activity.min_capacity:
            raise MinimumCapacityNotReached(activity, participants)

    # Remove overbooking
    reduce_overbooking(assignment, activities)

    return assignment
