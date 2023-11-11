import pytest

from activity import Activity, ActivityIDGenerator, InvalidGradeAccessError, Timespan
from dataclasses import asdict


def test_id_generation():
    assert Activity(name="A").id == 1
    assert Activity(name="B").id == 2
    assert ActivityIDGenerator().get_current_id() == 3
    ActivityIDGenerator().reset()
    assert ActivityIDGenerator().get_current_id() == 1
    assert Activity(name="C").id == 1


def test_activity_dict_conversion(example_activities):
    activity = example_activities[0]
    assert activity == Activity.from_dict(asdict(activity))


def test_grade_validity():
    activity = Activity(name="A")

    activity.set_grade_validity(1, False)
    activity.set_grade_validity(2, False)

    assert not activity.is_valid_grade(1)
    assert not activity.is_valid_grade(2)
    assert activity.is_valid_grade(3)
    assert activity.is_valid_grade(4)


def test_invalid_grade_access():
    with pytest.raises(InvalidGradeAccessError):
        Activity(name="A").set_grade_validity(5, False)

    with pytest.raises(InvalidGradeAccessError):
        Activity(name="A").set_grade_validity(0, False)


def test_timeslot_overlap():
    assert not Timespan.overlap(Timespan(17, 32), Timespan(33, 40))
    assert not Timespan.overlap(Timespan(1, 10), Timespan(20, 20))
    assert not Timespan.overlap(Timespan(1, 1), Timespan(2, 2))
    assert not Timespan.overlap(Timespan(1, 5), Timespan(5, 10))
    assert Timespan.overlap(Timespan(1, 5), Timespan(4, 6))
    assert Timespan.overlap(Timespan(1, 5), Timespan(1, 6))
    assert Timespan.overlap(Timespan(3, 5), Timespan(1, 5))
    assert Timespan.overlap(Timespan(10, 15), Timespan(12, 14))
    assert Timespan.overlap(Timespan(10, 15), Timespan(9, 16))


def test_activities_overlap():
    assert not Activity.overlap(
        Activity(name="A", timespan=Timespan(1, 5)),
        Activity(name="B", timespan=Timespan(6, 10)),
    )
    assert Activity.overlap(
        Activity(name="A", timespan=Timespan(1, 5)),
        Activity(name="B", timespan=Timespan(4, 10)),
    )
