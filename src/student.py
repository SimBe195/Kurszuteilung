from dataclasses import dataclass, field

from dataclasses_json import dataclass_json
from singleton_decorator import singleton

from id_generator import IDGenerator, ID


@singleton
class StudentIDGenerator(IDGenerator):
    pass


@dataclass_json
@dataclass
class Student:
    name: str
    grade: int
    subgrade: str
    preferences: dict[ID, int] = field(default_factory=dict)
    id: int = field(default_factory=StudentIDGenerator().get_next_id)


def get_student_id_map(students: list[Student]) -> dict[ID, Student]:
    return {student.id: student for student in students}
