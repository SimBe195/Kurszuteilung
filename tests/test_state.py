import os.path
from pathlib import Path

from activity import ActivityIDGenerator
from state import State
from student import StudentIDGenerator


def test_state_reset(example_students, example_activities, example_assignment, example_state):
    assert example_state.students == example_students
    assert example_state.activities == example_activities
    assert example_state.assignment == example_assignment
    example_state.reset()
    assert example_state.students != example_students
    assert example_state.activities != example_activities
    assert example_state.assignment != example_assignment


def test_global_student_id_reset(example_students):
    state = State()

    assert StudentIDGenerator().get_current_id() == len(example_students) + 1
    state.set_students(example_students)
    assert StudentIDGenerator().get_current_id() == len(example_students) + 1
    state.reset()
    assert StudentIDGenerator().get_current_id() == 1


def test_global_activity_id_reset(example_activities):
    state = State()

    assert ActivityIDGenerator().get_current_id() == len(example_activities) + 1
    state.set_activities(example_activities)
    assert ActivityIDGenerator().get_current_id() == len(example_activities) + 1
    state.set_activities([])
    assert ActivityIDGenerator().get_current_id() == 1


def test_state_dict_conversion(example_students, example_activities, example_assignment):
    state = State()
    state.set_students(example_students).set_activities(example_activities).set_assignment(example_assignment)
    state_dict = state.as_dict()

    state.reset()
    assert example_students != state.students
    assert example_activities != state.activities
    assert example_assignment != state.assignment

    state.from_dict(state_dict)
    assert example_students == state.students
    assert example_activities == state.activities
    assert example_assignment == state.assignment


def test_state_write_read(example_students, example_activities, example_assignment):
    test_path = Path("testfile.json")
    state = State().set_students(example_students).set_activities(example_activities).set_assignment(example_assignment)

    assert example_students == state.students
    assert example_activities == state.activities
    assert example_assignment == state.assignment

    state.write(test_path)

    assert os.path.exists(test_path)

    state.reset()

    assert example_students != state.students
    assert example_activities != state.activities
    assert example_assignment != state.assignment

    state.read(test_path)

    assert example_students == state.students
    assert example_activities == state.activities
    assert example_assignment == state.assignment

    os.remove(test_path)
