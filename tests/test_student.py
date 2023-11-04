from dataclasses import asdict

from student import Student


def test_student_dict_conversion(example_students):
    student = example_students[0]
    assert student == Student.from_dict(asdict(student))
