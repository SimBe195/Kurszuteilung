import assignment as assign_mod
import pytest

from activity import Activity
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
    with pytest.raises(assign_mod.StudentIDDoesNotExist):
        example_assignment.remove_student_from_activity_by_id(-1, 1)


def test_remove_from_non_assigned_activity(example_assignment):
    with pytest.raises(assign_mod.NotAssignedToActivity):
        example_assignment.remove_student_from_activity_by_id(1, -1)


def test_assign_bad_grade():
    assignment = assign_mod.Assignment()
    student = Student(name="A", grade=1, subgrade="a", preferences=[1])
    activity = Activity(name="A", supervisor="S", valid_grades=[False, True, True, True])

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
    with pytest.raises(assign_mod.ActivityIDDoesNotExist):
        assignment.participant_count(2)


def test_assign_validity(example_students, example_activities, example_assignment):
    example_assignment.check_validity(example_students, example_activities)


def test_assign_validity_grade_restriction_violation():
    activity = Activity(name="A", supervisor="S", valid_grades=[True, False, True, True])
    student = Student(name="A", grade=2, subgrade="a", preferences=[activity.id])
    assignment = assign_mod.Assignment()
    assignment.assign_student_to_activity_by_id(student.id, activity.id)
    with pytest.raises(assign_mod.GradeRestrictionViolation):
        assignment.check_validity([student], [activity])


def test_assign_validity_min_capacity_violation():
    activity = Activity(name="A", supervisor="S", min_capacity=2)
    student = Student(name="A", grade=2, subgrade="a", preferences=[activity.id])
    assignment = assign_mod.Assignment()
    assignment.assign_student_to_activity(student, activity)
    with pytest.raises(assign_mod.MinimumCapacityNotReached):
        assignment.check_validity([student], [activity])


def test_assign_validity_max_capacity_violation():
    activity = Activity(name="A", supervisor="S", max_capacity=1)
    student_1 = Student(name="A", grade=2, subgrade="a", preferences=[activity.id])
    student_2 = Student(name="B", grade=3, subgrade="a", preferences=[activity.id])
    assignment = assign_mod.Assignment()
    assignment.assign_student_to_activity(student_1, activity)
    assignment.assign_student_to_activity(student_2, activity)
    with pytest.raises(assign_mod.MaximumCapacityReached):
        assignment.check_validity([student_1, student_2], [activity])


def test_assign_validity_preference_violation():
    activity = Activity(name="A", supervisor="S", max_capacity=1)
    student = Student(name="A", grade=2, subgrade="a", preferences=[activity.id + 1])
    assignment = assign_mod.Assignment()
    assignment.assign_student_to_activity(student, activity)
    with pytest.raises(assign_mod.ActivityNotPreferred):
        assignment.check_validity([student], [activity])


def test_assign_validity_no_assignment(example_students, example_activities):
    student = example_students[0]
    activity = example_activities[0]
    assignment = assign_mod.Assignment()
    assignment.assign_student_to_activity(student, activity)
    assignment.remove_student_from_activity_by_id(student.id, activity.id)
    with pytest.raises(assign_mod.NoAssignedActivity):
        assignment.check_validity([student], [activity])


def test_auto_assign(example_students, example_activities, example_assignment):
    assignment = assign_mod.assign_students(example_students, example_activities)
    assert assignment == example_assignment


def test_auto_assign_overbooked():
    activities = [
        Activity(name="A", supervisor="S", min_capacity=1, max_capacity=1),
        Activity(name="B", supervisor="T", min_capacity=0, max_capacity=2),
    ]
    students = [
        Student(name="A", grade=1, subgrade="a", preferences=[activities[0].id, activities[1].id]),
        Student(name="B", grade=1, subgrade="a", preferences=[activities[0].id]),
        Student(name="C", grade=1, subgrade="a", preferences=[activities[0].id, activities[1].id]),
    ]
    assignment = assign_mod.assign_students(students, activities)
    assert set(assignment.get_students_for_activity(activities[0].id)) == {students[1].id}
    assert set(assignment.get_students_for_activity(activities[1].id)) == {students[0].id, students[2].id}


def test_auto_assign_non_existing_preference(example_students, example_activities, example_assignment):
    example_students[0].preferences.append(-1)
    with pytest.raises(assign_mod.ActivityIDDoesNotExist):
        assign_mod.assign_students(example_students, example_activities)


def test_auto_assign_minimum_capacity_violation(example_students, example_activities):
    example_activities[0].min_capacity = 5
    with pytest.raises(assign_mod.MinimumCapacityNotReached):
        assign_mod.assign_students(example_students, example_activities)


def test_auto_assign_maximum_capacity_violation():
    activity = Activity(name="A", supervisor="S", max_capacity=1)
    students = [
        Student(name="A", grade=1, subgrade="a", preferences=[activity.id]),
        Student(name="B", grade=1, subgrade="a", preferences=[activity.id]),
        Student(name="C", grade=1, subgrade="a", preferences=[activity.id]),
    ]
    with pytest.raises(assign_mod.MaximumCapacityReached):
        assign_mod.assign_students(students, [activity])
