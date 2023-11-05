from activity import Activity
from assignment import assign_students
from gui import run
from state import State
from student import Student


def main() -> None:
    state = State()

    state.add_student(Student(name="Alice", grade=1, subgrade="a", preferences=[1]))
    state.add_student(Student(name="Alice", grade=1, subgrade="a", preferences=[1]))
    state.add_student(Student(name="Bob", grade=2, subgrade="b", preferences=[1, 2]))
    state.add_student(Student(name="Alice", grade=1, subgrade="a", preferences=[1]))
    state.add_student(Student(name="Bob", grade=2, subgrade="b", preferences=[1, 2]))
    state.add_student(Student(name="Alice", grade=1, subgrade="a", preferences=[1]))
    state.add_student(Student(name="Bob", grade=2, subgrade="b", preferences=[1, 2]))
    state.add_student(Student(name="Alice", grade=1, subgrade="a", preferences=[1]))
    state.add_student(Student(name="Bob", grade=2, subgrade="b", preferences=[1, 2]))
    state.add_student(Student(name="Alice", grade=1, subgrade="a", preferences=[1]))
    state.add_student(Student(name="Bob", grade=2, subgrade="b", preferences=[1, 2]))
    state.add_student(Student(name="Alice", grade=1, subgrade="a", preferences=[1]))
    state.add_student(Student(name="Bob", grade=2, subgrade="b", preferences=[1, 2]))
    state.add_student(Student(name="Alice", grade=1, subgrade="a", preferences=[1]))
    state.add_student(Student(name="Bob", grade=2, subgrade="b", preferences=[1, 2]))
    state.add_student(Student(name="Bob", grade=2, subgrade="b", preferences=[1, 2]))

    state.add_activity(
        Activity(
            name="Malen", supervisor="Sabine", min_capacity=1, max_capacity=10, valid_grades=[True, True, False, False]
        )
    )
    state.add_activity(
        Activity(
            name="Turnen",
            supervisor="Thorsten",
            min_capacity=1,
            max_capacity=10,
            valid_grades=[False, True, True, True],
        )
    )
    # state.set_assignment(assign_students(state.students, state.activities))
    run()


if __name__ == "__main__":
    main()
