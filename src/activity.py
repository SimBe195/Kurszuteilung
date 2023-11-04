from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from singleton_decorator import singleton

from id_generator import IDGenerator, ID


@singleton
class ActivityIDGenerator(IDGenerator):
    pass


class InvalidGradeAccessError(Exception):
    def __init__(self, grade: int):
        super().__init__(f"Grade must be between 1 and 4; received {grade}.")


@dataclass_json
@dataclass
class Activity:
    name: str
    supervisor: str
    min_capacity: int = 0
    max_capacity: int = float("inf")
    valid_grades: list[bool] = field(default_factory=lambda: [True] * 4)
    id: ID = field(default_factory=ActivityIDGenerator().get_next_id)

    def set_grade_validity(self, grade: int, valid: bool) -> None:
        if not 1 <= grade <= 4:
            raise InvalidGradeAccessError(grade)

        self.valid_grades[grade - 1] = valid

    def is_valid_grade(self, grade: int) -> bool:
        if not 1 <= grade <= 4:
            raise InvalidGradeAccessError(grade)

        return self.valid_grades[grade - 1]
