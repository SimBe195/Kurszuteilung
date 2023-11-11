from activity import Activity, Timespan
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
            name="Malen",
            min_capacity=1,
            max_capacity=10,
            timespan=Timespan.from_day_hour_minute(0, 8, 0, 0, 9, 30),
            valid_grades=[True, True, False, False],
        )
    )
    state.add_activity(
        Activity(
            name="Turnen",
            min_capacity=1,
            max_capacity=10,
            timespan=Timespan.from_day_hour_minute(1, 10, 15, 1, 11, 45),
            valid_grades=[False, True, True, True],
        )
    )
    # state.set_assignment(assign_students(state.students, state.activities))
    run()


if __name__ == "__main__":
    main()
