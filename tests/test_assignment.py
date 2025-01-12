import assignment as assign_mod
import pytest

from activity import Activity, Timespan
from student import Student


def test_assignment_dict_conversion(example_assignment):
    assert example_assignment == assign_mod.Assignment.from_dict(example_assignment.as_dict())


def test_assign_by_id():
    assignment = assign_mod.Assignment()
    assignment.assign_student_to_activity_by_id(1, 2)
    assert set(assignment.get_activities_for_student(1)) == {2}
    assert set(assignment.get_students_for_activity(2)) == {1}


def test_assign_remove(example_students, example_activities):
    assignment = assign_mod.Assignment()
    student = example_students[0]
    activity = example_activities[0]
    assignment.assign_student_to_activity(student, activity)
    assert set(assignment.get_activities_for_student(student.id)) == {activity.id}
    assert set(assignment.get_students_for_activity(activity.id)) == {student.id}
    assignment.remove_student_from_activity_by_id(student.id, activity.id)
    assert len(assignment.get_activities_for_student(student.id)) == 0
    assert len(assignment.get_students_for_activity(activity.id)) == 0


def test_remove_non_existing_student(example_assignment):
    with pytest.raises(assign_mod.StudentIDNotAssigned):
        example_assignment.remove_student_from_activity_by_id(-1, 1)


def test_remove_from_non_assigned_activity(example_assignment):
    with pytest.raises(assign_mod.NotAssignedToActivity):
        example_assignment.remove_student_from_activity_by_id(1, -1)


def test_assign_bad_grade():
    assignment = assign_mod.Assignment()
    student = Student(name="A", grade=1, subgrade="a", preferences={1: 1})
    activity = Activity(name="A", valid_grades=[False, True, True, True])

    with pytest.raises(assign_mod.GradeRestrictionViolation):
        assignment.assign_student_to_activity(student, activity)


def test_participant_count():
    assignment = assign_mod.Assignment()
    assignment.assign_student_to_activity_by_id(1, 1)
    assignment.assign_student_to_activity_by_id(2, 1)
    assignment.assign_student_to_activity_by_id(3, 1)
    assignment.assign_student_to_activity_by_id(4, 2)
    assert assignment.participant_count(1) == 3
    assert assignment.participant_count(2) == 1


def test_participant_count_invalid_id():
    assignment = assign_mod.Assignment()
    assignment.assign_student_to_activity_by_id(1, 1)
    assert assignment.participant_count(2) == 0


def test_assign_validity(example_students, example_activities, example_assignment):
    example_assignment.check_validity(example_students, example_activities)


def test_assign_validity_grade_restriction_violation():
    activity = Activity(name="A", valid_grades=[True, False, True, True])
    student = Student(name="A", grade=2, subgrade="a", preferences={activity.id: 1})
    assignment = assign_mod.Assignment()
    assignment.assign_student_to_activity_by_id(student.id, activity.id)
    exceptions = assignment.check_validity([student], [activity])
    assert any(isinstance(e, assign_mod.GradeRestrictionViolation) for e in exceptions)


def test_assign_validity_min_capacity_violation():
    activity = Activity(name="A", min_capacity=2)
    student = Student(name="A", grade=2, subgrade="a", preferences={activity.id: 1})
    assignment = assign_mod.Assignment()
    assignment.assign_student_to_activity(student, activity)
    exceptions = assignment.check_validity([student], [activity])
    assert any(isinstance(e, assign_mod.MinimumCapacityNotReached) for e in exceptions)


def test_assign_validity_max_capacity_violation():
    activity = Activity(name="A", max_capacity=1)
    student_1 = Student(name="A", grade=2, subgrade="a", preferences={activity.id: 1})
    student_2 = Student(name="B", grade=3, subgrade="a", preferences={activity.id: 1})
    assignment = assign_mod.Assignment()
    assignment.assign_student_to_activity(student_1, activity)
    with pytest.raises(assign_mod.MaximumCapacityReached):
        assignment.assign_student_to_activity(student_2, activity)


def test_assign_validity_preference_violation():
    activity = Activity(name="A", max_capacity=1)
    student = Student(name="A", grade=2, subgrade="a", preferences={activity.id + 1: 1})
    assignment = assign_mod.Assignment()
    with pytest.raises(assign_mod.ActivityNotPreferred):
        assignment.assign_student_to_activity(student, activity)


def test_assign_validity_no_assignment(example_students, example_activities):
    student = example_students[0]
    activity = example_activities[0]
    assignment = assign_mod.Assignment()
    assignment.assign_student_to_activity(student, activity)
    assignment.remove_student_from_activity_by_id(student.id, activity.id)
    exceptions = assignment.check_validity([student], [activity])
    assert any(isinstance(e, assign_mod.NoAssignedActivity) for e in exceptions)


def test_auto_assign(example_students, example_activities, example_assignment):
    assignment = assign_mod.assign_students(example_students, example_activities)
    assert assignment == example_assignment


def test_auto_assign_overbooked():
    activities = [
        Activity(name="A", min_capacity=1, max_capacity=1),
        Activity(name="B", min_capacity=0, max_capacity=2),
    ]
    students = [
        Student(name="A", grade=1, subgrade="a", preferences={activities[0].id: 1, activities[1].id: 1}),
        Student(name="B", grade=1, subgrade="a", preferences={activities[0].id: 1}),
        Student(name="C", grade=1, subgrade="a", preferences={activities[0].id: 1, activities[1].id: 1}),
    ]
    assignment = assign_mod.assign_students(students, activities)
    assert set(assignment.get_students_for_activity(activities[0].id)) == {students[1].id}
    assert set(assignment.get_students_for_activity(activities[1].id)) == {students[0].id, students[2].id}


def test_auto_assign_overbooked_all_max_capacity():
    activities = [
        Activity(name="A", min_capacity=0, max_capacity=2),
        Activity(name="B", min_capacity=0, max_capacity=3),
    ]
    students = [
        Student(name="A", grade=1, subgrade="a", preferences={activities[0].id: 1, activities[1].id: 1}),
        Student(name="B", grade=1, subgrade="a", preferences={activities[0].id: 1}),
        Student(name="C", grade=1, subgrade="a", preferences={activities[0].id: 1, activities[1].id: 1}),
        Student(name="D", grade=1, subgrade="a", preferences={activities[0].id: 1, activities[1].id: 1}),
    ]
    assignment = assign_mod.assign_students(students, activities)
    assert len(assignment.get_students_for_activity(activities[0].id)) == activities[0].max_capacity
    assert len(assignment.get_students_for_activity(activities[1].id)) == activities[1].max_capacity


def test_auto_assign_non_existing_preference(example_students, example_activities, example_assignment):
    example_students[0].preferences[-1] = 1
    with pytest.raises(assign_mod.ActivityIDNotAssigned):
        assign_mod.assign_students(example_students, example_activities)


def test_auto_assign_minimum_capacity_violation(example_students, example_activities):
    example_activities[0].min_capacity = 5
    assignment = assign_mod.assign_students(example_students, example_activities)
    exceptions = assignment.check_validity(example_students, example_activities)
    assert any(isinstance(e, assign_mod.MinimumCapacityNotReached) for e in exceptions)


def test_auto_assign_maximum_capacity_violation():
    activity = Activity(name="A", max_capacity=1)
    students = [
        Student(name="A", grade=1, subgrade="a", preferences={activity.id: 1}),
        Student(name="B", grade=1, subgrade="a", preferences={activity.id: 1}),
        Student(name="C", grade=1, subgrade="a", preferences={activity.id: 1}),
    ]
    assignment = assign_mod.assign_students(students, [activity])
    exceptions = assignment.check_validity(students, [activity])
    assert any(isinstance(e, assign_mod.StudentIDNotAssigned) for e in exceptions)


def test_overbooking_and_capacity_constraints():
    activities = [
        Activity(
            name="A",
            min_capacity=1,
            max_capacity=2,
            timespan=Timespan.from_day_hour_minute(0, 9, 0, 0, 10, 0),
        ),
        Activity(
            name="B",
            min_capacity=1,
            max_capacity=1,
            timespan=Timespan.from_day_hour_minute(0, 10, 0, 0, 11, 0),
        ),
    ]
    students = [
        Student(name="A", grade=1, subgrade="a", preferences={1: 1, 2: 1}),
        Student(name="B", grade=1, subgrade="a", preferences={1: 1}),
        Student(name="C", grade=1, subgrade="a", preferences={1: 1, 2: 1}),
    ]
    assignment = assign_mod.assign_students(students, activities)
    assert assignment.participant_count(1) <= activities[0].max_capacity
    assert assignment.participant_count(2) <= activities[1].max_capacity


def test_timing_conflicts():
    activities = [
        Activity(
            name="A",
            min_capacity=1,
            max_capacity=2,
            timespan=Timespan.from_day_hour_minute(0, 9, 0, 0, 10, 0),
        ),
        Activity(
            name="B",
            min_capacity=1,
            max_capacity=2,
            timespan=Timespan.from_day_hour_minute(0, 9, 30, 0, 10, 30),
        ),
    ]
    students = [
        Student(name="A", grade=1, subgrade="a", preferences={1: 1, 2: 1}),
        Student(name="B", grade=1, subgrade="a", preferences={1: 1, 2: 1}),
    ]
    assignment = assign_mod.assign_students(students, activities)
    assert len(assignment.get_activities_for_student(students[0].id)) == 1
    assert len(assignment.get_activities_for_student(students[1].id)) == 1


def test_invalid_preference_assignment():
    activities = [
        Activity(
            name="A",
            min_capacity=1,
            max_capacity=2,
            valid_grades=[False, True, True, True],
        ),
        Activity(
            name="B",
            min_capacity=1,
            max_capacity=2,
            valid_grades=[True, True, True, True],
        ),
    ]
    students = [
        Student(
            name="A", grade=1, subgrade="a", preferences={1: 1, 2: 1}
        ),  # Preference for activity 0 but not allowed there
        Student(name="B", grade=2, subgrade="a", preferences={1: 1, 2: 1}),
    ]
    assignment = assign_mod.assign_students(students, activities)
    assert set(assignment.get_activities_for_student(students[0].id)) == {activities[1].id}
    assert set(assignment.get_activities_for_student(students[1].id)) == {activities[0].id, activities[1].id}


def test_auto_assign_weighted():
    students = [
        Student(name="A", grade=1, subgrade="a", preferences={1: 1, 2: 2}),
        Student(name="B", grade=2, subgrade="b", preferences={1: 2, 2: 1}),
    ]
    activities = [
        Activity(name="A", max_capacity=1),
        Activity(name="B", max_capacity=1),
    ]

    target_assignment = assign_mod.Assignment()
    target_assignment.assign_student_to_activity_by_id(1, 1)
    target_assignment.assign_student_to_activity_by_id(2, 2)

    assignment = assign_mod.assign_students(students, activities)
    assert assignment == target_assignment

    students[0].preferences = {1: 2, 2: 1}
    students[1].preferences = {1: 1, 2: 2}

    target_assignment = assign_mod.Assignment()
    target_assignment.assign_student_to_activity_by_id(1, 2)
    target_assignment.assign_student_to_activity_by_id(2, 1)

    assignment = assign_mod.assign_students(students, activities)
    assert assignment == target_assignment
