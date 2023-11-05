from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.pdfgen import canvas

from activity import Activity
from assignment import Assignment
from student import Student


def add_bullet_point(canv: canvas.Canvas, text: str, x: int, y: int, bullet_char: str = "-"):
    canv.drawString(x, y, bullet_char)
    canv.drawString(x + 15, y, text)


def create_student_assignment_pdf(
    students: list[Student], activities: list[Activity], assignment: Assignment, path: Path
):
    activity_id_map = {activity.id: activity for activity in activities}
    canv = canvas.Canvas(path.as_posix(), pagesize=A4)
    canv.setTitle("Document Title")

    students_per_page = 2

    for idx, student in enumerate(students, start=0):
        y_high = A4[1] - (idx % students_per_page) * (A4[1] // students_per_page)
        canv.setFont("Helvetica-Bold", 14)
        canv.drawString(
            2 * cm, y_high - 2 * cm, f"Kurszuteilung für {student.name} ({student.grade}{student.subgrade})"
        )

        canv.setFont("Helvetica", 12)
        intro_text = canv.beginText(2 * cm, y_high - 3 * cm)
        intro_text.textLine(f"Liebe Eltern von {student.name},")
        intro_text.textLine("")
        intro_text.textLine("Hiermit teilen wir Ihnen mit, dass ihr Kind zu den folgenden Kursaktivitäten")
        intro_text.textLine("angemeldet ist:")
        canv.drawText(intro_text)

        for num, activity_id in enumerate(assignment.get_activities_for_student(student.id)):
            activity = activity_id_map[activity_id]
            add_bullet_point(
                canv, f"{activity.name}, betreut von {activity.supervisor}.", 2.5 * cm, y_high - 5.5 * cm - num * cm
            )

        outro_text = canv.beginText(2 * cm, y_high - 9 * cm)
        outro_text.textLine("Im Falle von Fragen oder geänderten Abholzeiten informieren Sie uns bitte per E-Mail")
        outro_text.textOut("unter ")
        outro_text.setFillColor(colors.blue)
        outro_text.textOut("ogs.hoefchensweg@invia-aachen.de.")
        outro_text.setFillColor(colors.black)
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
