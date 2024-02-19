from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from operator import attrgetter

from reportlab.platypus import Table

from activity import Activity, get_activity_id_map
from assignment import Assignment
from student import Student, get_student_id_map


def add_bullet_point(canv: canvas.Canvas, text: str, x: int, y: int, bullet_char: str = "-"):
    canv.drawString(x, y, bullet_char)
    canv.drawString(x + 15, y, text)


def create_student_assignment_pdf(
    students: list[Student], activities: list[Activity], assignment: Assignment, path: Path
):
    activity_id_map = get_activity_id_map(activities)
    canv = canvas.Canvas(path.as_posix(), pagesize=A4)
    canv.setTitle("Kinderzuteilungen")

    students_per_page = 2

    for idx, student in enumerate([student for student in students if assignment.student_known(student.id)]):
        y_high = A4[1] - (idx % students_per_page) * (A4[1] // students_per_page)
        canv.setFont("Helvetica-Bold", 14)
        canv.drawString(
            2 * cm, y_high - 2 * cm, f"Kurszuteilung für {student.name} ({student.grade}{student.subgrade})"
        )

        canv.setFont("Helvetica", 12)
        intro_text = canv.beginText(2 * cm, y_high - 3 * cm)
        intro_text.textLine(f"Liebe Eltern von {student.name},")
        intro_text.textLine("")
        intro_text.textLine("Hiermit teilen wir Ihnen mit, dass Ihr Kind zu den folgenden Kursaktivitäten")
        intro_text.textLine("angemeldet ist:")
        canv.drawText(intro_text)

        for num, activity_id in enumerate(assignment.get_activities_for_student(student.id)):
            activity = activity_id_map[activity_id]
            add_bullet_point(
                canv, f"{activity.name} ({activity.timespan})", 2.5 * cm, y_high - 5.3 * cm - num * 0.8 * cm
            )

        outro_text = canv.beginText(2 * cm, y_high - 9 * cm)
        outro_text.textLine("Im Falle von Fragen oder geänderten Abholzeiten informieren Sie uns bitte per E-Mail")
        outro_text.textOut("unter ")
        # outro_text.setFillColor(colors.blue)
        outro_text.textOut("ogs.hoefchensweg@invia-aachen.de.")
        # outro_text.setFillColor(colors.black)
        outro_text.textLine("")
        outro_text.textLine("")
        outro_text.textLine("")
        outro_text.textLine("Mit freundlichen Grüßen")
        outro_text.textLine("")
        outro_text.textLine("Ihr OGS-Team")
        canv.drawText(outro_text)

        if idx % students_per_page == students_per_page - 1:
            canv.showPage()
    canv.save()


def create_course_assignment_pdf(
    students: list[Student], activities: list[Activity], assignment: Assignment, path: Path
):
    student_id_map = get_student_id_map(students)
    canv = canvas.Canvas(path.as_posix(), pagesize=A4)
    canv.setTitle("Kurszuteilungen")

    activities_per_page = 2

    for idx, activity in enumerate(activities):
        y_high = A4[1] - (idx % activities_per_page) * (A4[1] // activities_per_page)

        canv.setFont("Helvetica", 12)
        intro_text = canv.beginText(2 * cm, y_high - 2 * cm)
        intro_text.textLine("Folgende Kinder sind zur Kursaktivität")
        intro_text.textLine("")
        intro_text.setFont("Helvetica-Bold", 12)
        intro_text.textOut(f"  {activity.name} ")
        intro_text.setFont("Helvetica", 12)
        intro_text.textLine(f"({str(activity.timespan)})")
        intro_text.textLine("")
        intro_text.textLine("angemeldet:")
        canv.drawText(intro_text)

        students = [student_id_map[student_id] for student_id in assignment.get_students_for_activity(activity.id)]
        sorted_students = sorted(students, key=attrgetter("grade", "subgrade", "name"))

        columns = 2
        rows = -(len(students) // -columns)

        for num, student in enumerate(sorted_students):
            x = 2.5 * cm + (num // rows) * ((A4[0] - 5 * cm) // columns)
            y = y_high - 5 * cm - (num % rows) * 0.8 * cm
            add_bullet_point(canv, f"{student.name} ({student.grade}{student.subgrade})", x, y)

        if idx % activities_per_page == activities_per_page - 1:
            canv.showPage()
    canv.save()


def create_course_attendance_list_pdf(
    students: list[Student], activities: list[Activity], assignment: Assignment, path: Path
):
    student_id_map = get_student_id_map(students)
    canv = canvas.Canvas(path.as_posix(), pagesize=A4)
    canv.setTitle("Anwesenheitsliste")

    for idx, activity in enumerate(activities):
        y_high = A4[1]

        canv.setFont("Helvetica", 12)
        intro_text = canv.beginText(2 * cm, y_high - 2 * cm)
        intro_text.textLine("Anwesenheitsliste für Kurs")
        intro_text.textLine("")
        intro_text.setFont("Helvetica-Bold", 12)
        intro_text.textOut(f"  {activity.name} ")
        intro_text.setFont("Helvetica", 12)
        intro_text.textLine(f"({str(activity.timespan)}):")
        canv.drawText(intro_text)

        date_columns = 10
        empty_rows = 5

        students = [student_id_map[student_id] for student_id in assignment.get_students_for_activity(activity.id)]
        sorted_students = sorted(students, key=attrgetter("grade", "subgrade", "name"))

        data = (
            [["Datum:"] + [""] * date_columns]
            + [
                [f"{student.name} ({student.grade}{student.subgrade})"] + ([""] * date_columns)
                for student in sorted_students
            ]
            + [[""] * (date_columns + 1)] * empty_rows
        )

        t = Table(
            data,
            [4 * cm] + ([(A4[0] - 8 * cm) / date_columns] * date_columns),
            [0.75 * cm] * len(data),
            style=[
                ("GRID", (0, 0), (-1, -1), 0.5, colors.dimgray),
                ("LINEBELOW", (0, 0), (-1, 0), 1, colors.black),
                ("LINEAFTER", (0, 0), (0, -1), 1, colors.black),
                ("FONTNAME", (0, 0), (0, 0), "Helvetica-Bold"),
            ],
        )

        t.wrapOn(canv, 0, 0)
        t.drawOn(canv, x=2 * cm, y=y_high - 4 * cm - 0.75 * cm * len(data))

        canv.showPage()
    canv.save()
