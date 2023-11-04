import pytest

from activity import Activity, ActivityIDGenerator, InvalidGradeAccessError
from dataclasses import asdict


def test_id_generation():
    assert Activity(name="A", supervisor="S").id == 1
    assert Activity(name="B", supervisor="S").id == 2
    assert ActivityIDGenerator().get_current_id() == 3
    ActivityIDGenerator().reset()
    assert ActivityIDGenerator().get_current_id() == 1
    assert Activity(name="C", supervisor="S").id == 1


def test_activity_dict_conversion(example_activities):
    activity = example_activities[0]
    assert activity == Activity.from_dict(asdict(activity))


def test_grade_validity():
    activity = Activity(name="A", supervisor="S")

    activity.set_grade_validity(1, False)
    activity.set_grade_validity(2, False)

    assert not activity.is_valid_grade(1)
    assert not activity.is_valid_grade(2)
    assert activity.is_valid_grade(3)
    assert activity.is_valid_grade(4)


def test_invalid_grade_access():
    with pytest.raises(InvalidGradeAccessError):
        Activity(name="A", supervisor="S").set_grade_validity(5, False)

    with pytest.raises(InvalidGradeAccessError):
        Activity(name="A", supervisor="S").set_grade_validity(0, False)
