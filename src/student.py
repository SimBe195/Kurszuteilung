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
    preferences: list[ID] = field(default_factory=list)
    id: int = field(default_factory=StudentIDGenerator().get_next_id)
