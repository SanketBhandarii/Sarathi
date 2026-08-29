from __future__ import annotations

from datetime import date

from pydantic import BaseModel, computed_field

from app.student.profile import Category, StudentProfile

CATEGORY_ON_FORMS: dict[Category, str] = {
    Category.UR: "UR / General",
    Category.OBC: "OBC (Non-Creamy Layer)",
    Category.SC: "SC",
    Category.ST: "ST",
    Category.EWS: "EWS",
}


class FormField(BaseModel):
    label: str
    value: str
    note: str | None = None
    needs_you: bool = False


class FormPack(BaseModel):
    student_name: str
    exam_name: str
    fields: list[FormField] = []

    @computed_field
    @property
    def ready_count(self) -> int:
        return len([f for f in self.fields if not f.needs_you])

    @computed_field
    @property
    def needs_you_count(self) -> int:
        return len([f for f in self.fields if f.needs_you])


def _percentage_note(profile: StudentProfile) -> str | None:
    if profile.education.percentage is None:
        return None
    return (
        "If your marksheet shows CGPA, most forms want the percentage. "
        "Use the conversion printed by your university, not a guess."
    )


def build_form_pack(profile: StudentProfile, exam_name: str, today: date) -> FormPack:
    education = profile.education
    fields = [
        FormField(label="Full name", value=profile.name),
        FormField(
            label="Date of birth",
            value=profile.date_of_birth.strftime("%d/%m/%Y"),
            note="Written exactly as on your 10th standard certificate.",
        ),
        FormField(label="Category", value=CATEGORY_ON_FORMS[profile.category]),
        FormField(label="Gender", value=profile.gender.value.title()),
        FormField(label="State of domicile", value=profile.state),
        FormField(label="District", value=profile.district),
        FormField(label="Highest qualification", value=education.degree),
    ]

    if education.stream:
        fields.append(FormField(label="Stream / discipline", value=education.stream))
    if education.completed_year:
        fields.append(FormField(label="Year of passing", value=str(education.completed_year)))
    if education.percentage is not None:
        fields.append(
            FormField(
                label="Percentage of marks",
                value=f"{education.percentage:g}%",
                note=_percentage_note(profile),
            )
        )

    fields.append(
        FormField(
            label="Age as on today",
            value=f"{profile.age_on(today):.0f} years",
            note="Each exam counts age on its own date. Check the notification.",
        )
    )

    for label, note in [
        ("Mobile number", "Use a number you will keep for the next two years."),
        ("Email address", "The commission sends the admit card here."),
        ("Address for communication", "As on the document you will show at the centre."),
    ]:
        fields.append(FormField(label=label, value="", note=note, needs_you=True))

    return FormPack(student_name=profile.name, exam_name=exam_name, fields=fields)
