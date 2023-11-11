from __future__ import annotations

from dataclasses import dataclass, field

from dataclasses_json import dataclass_json
from singleton_decorator import singleton

from id_generator import IDGenerator, ID


@singleton
class ActivityIDGenerator(IDGenerator):
    pass


class InvalidGradeAccessError(Exception):
    def __init__(self, grade: int):
        super().__init__(f"Klasse muss zwischen 1 und 4 sein; ist {grade}.")


WEEKDAYS = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]


@dataclass_json
@dataclass
class Timespan:
    from_slot: int
    to_slot: int

    def __post_init__(self):
        assert 0 <= self.from_slot <= self.to_slot < 672

    @classmethod
    def from_day_hour_minute(
        cls, from_day: int, from_hour: int, from_minute: int, to_day: int, to_hour: int, to_minute: int
    ) -> Timespan:
        assert from_minute % 15 == 0
        assert to_minute % 15 == 0
        from_slot = from_day * 96 + from_hour * 4 + from_minute // 15
        to_slot = to_day * 96 + to_hour * 4 + to_minute // 15
        return cls(from_slot, to_slot)

    @staticmethod
    def convert_to_day_hour_minute(timeslot: int) -> (int, int, int):
        minute = 15 * (timeslot % 4)
        hour = (timeslot // 4) % 24
        day = timeslot // 96

        return day, hour, minute

    def get_from_day_hour_minute(self) -> (int, int, int):
        return Timespan.convert_to_day_hour_minute(self.from_slot)

    def get_to_day_hour_minute(self) -> (int, int, int):
        return Timespan.convert_to_day_hour_minute(self.to_slot)

    def __str__(self):
        from_day, from_hour, from_minute = self.get_from_day_hour_minute()
        to_day, to_hour, to_minute = self.get_to_day_hour_minute()

        if from_day == to_day:
            return f"{WEEKDAYS[from_day]}, {from_hour:02d}:{from_minute:02d} Uhr - {to_hour:02d}:{to_minute:02d} Uhr"
        else:
            return (
                f"{WEEKDAYS[from_day]}, {from_hour:02d}:{from_minute:02d} Uhr - "
                f"{WEEKDAYS[to_day]}, {to_hour:02d}:{to_minute:02d} Uhr"
            )

    @staticmethod
    def overlap(timeslot_0: Timespan, timeslot_1: Timespan) -> bool:
        return not (timeslot_0.to_slot <= timeslot_1.from_slot or timeslot_1.to_slot <= timeslot_0.from_slot)


@dataclass_json
@dataclass
class Activity:
    name: str
    min_capacity: int = 0
    max_capacity: int = float("inf")
    timespan: Timespan = field(default_factory=lambda: Timespan(0, 0))
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

    @staticmethod
    def overlap(activity_0: Activity, activity_1: Activity) -> bool:
        return Timespan.overlap(activity_0.timespan, activity_1.timespan)


def get_activity_id_map(activities: list[Activity]) -> dict[ID, Activity]:
    return {activity.id: activity for activity in activities}
