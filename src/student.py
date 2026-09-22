from dataclasses import dataclass, field

from dataclasses_json import DataClassJsonMixin
from singleton_decorator import singleton

from id_generator import ID, IDGenerator


@singleton
class StudentIDGenerator(IDGenerator):
    pass


@dataclass
class Student(DataClassJsonMixin):
    name: str
    grade: int
    subgrade: str
    preferences: dict[ID, int] = field(default_factory=dict)
    id: int = field(default_factory=StudentIDGenerator().get_next_id)


def get_student_id_map(students: list[Student]) -> dict[ID, Student]:
    return {student.id: student for student in students}
