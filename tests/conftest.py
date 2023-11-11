import pytest

from activity import ActivityIDGenerator, Activity, Timespan
from assignment import Assignment
from state import State
from student import StudentIDGenerator, Student


@pytest.fixture(autouse=True)
def reset_id_generators() -> None:
    ActivityIDGenerator().reset()
    StudentIDGenerator().reset()


@pytest.fixture
def example_students() -> list[Student]:
    return [
        Student(name="A", grade=1, subgrade="a", preferences=[1, 2]),
        Student(name="B", grade=2, subgrade="b", preferences=[2]),
    ]


@pytest.fixture
def example_activities() -> list[Activity]:
    return [
        Activity(
            name="A", min_capacity=1, max_capacity=1, timespan=Timespan(32, 38), valid_grades=[True, True, True, True]
        ),
        Activity(
            name="B", min_capacity=0, max_capacity=2, timespan=Timespan(40, 44), valid_grades=[True, True, False, False]
        ),
    ]


@pytest.fixture
def example_assignment() -> Assignment:
    assignment = Assignment()
    assignment.assign_student_to_activity_by_id(1, 1)
    assignment.assign_student_to_activity_by_id(1, 2)
    assignment.assign_student_to_activity_by_id(2, 2)
    return assignment


@pytest.fixture
def example_state(example_students, example_activities, example_assignment):
    return State().set_students(example_students).set_activities(example_activities).set_assignment(example_assignment)
