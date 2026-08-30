from __future__ import annotations

from datetime import date

import pytest

from app.eligibility.levels import level_asked_for, satisfies
from app.eligibility.qualification import evaluate_qualification
from app.extraction.schema import Citation, ExamRules, Qualification
from app.student.profile import Education, StudentProfile
from app.student.qualifications import EducationHistory, Level, MarksKind
from app.student.qualifications import Qualification as Step

CITE = Citation(page=3, quote="Degree of a recognised University or Equivalent.")


def rules(requirement: str, minimum: float | None = None) -> ExamRules:
    return ExamRules(
        exam_name="Test", source_id="upsc", document_sha256="x",
        qualifications=[
            Qualification(requirement=requirement, minimum_percentage=minimum, citation=CITE)
        ],
    )


def student(*steps: Step) -> StudentProfile:
    return StudentProfile(
        name="T", date_of_birth=date(2004, 11, 14), state="Maharashtra", district="Nagpur",
        education=Education(degree="x", percentage=None),
        education_history=EducationHistory(entries=list(steps)),
    )


TENTH = Step(level=Level.CLASS_10, marks=78.4, is_completed=True)


@pytest.mark.parametrize(
    "text,expected",
    [
        ("Degree of a recognised University or Equivalent.", Level.GRADUATION),
        ("A Degree (Graduation) in any discipline", Level.GRADUATION),
        ("Bachelor's degree in any subject", Level.GRADUATION),
        ("Diploma in Civil Engineering", Level.DIPLOMA),
        ("Passed 12th standard or equivalent", Level.CLASS_12),
        ("10th standard pass with Maths and English", Level.CLASS_10),
        ("Master degree in the relevant subject", Level.POST_GRADUATION),
        ("ITI certificate in the relevant trade", Level.ITI),
    ],
)
def test_the_level_a_notification_asks_for_is_recognised(text, expected):
    assert level_asked_for(text) is expected


def test_a_diploma_does_not_satisfy_a_degree():
    assert satisfies(Level.DIPLOMA, Level.GRADUATION) is False


def test_a_degree_satisfies_a_lower_requirement():
    assert satisfies(Level.GRADUATION, Level.CLASS_12) is True
    assert satisfies(Level.GRADUATION, Level.CLASS_10) is True


def test_a_diploma_holder_is_blocked_from_a_degree_exam():
    reasons = evaluate_qualification(
        rules("Degree of a recognised University or Equivalent."),
        student(TENTH, Step(level=Level.DIPLOMA, marks=72.0, is_completed=True)),
    )
    blocking = [r for r in reasons if r.blocks_application]
    assert blocking, "a diploma must not pass a degree requirement"
    assert "needs graduation" in blocking[0].text
    assert "diploma" in blocking[0].text


def test_a_graduate_passes_a_degree_exam():
    reasons = evaluate_qualification(
        rules("Degree of a recognised University or Equivalent."),
        student(TENTH, Step(level=Level.GRADUATION, marks=64.0, is_completed=True)),
    )
    assert [r for r in reasons if r.blocks_application] == []


def test_an_unfinished_degree_blocks_but_says_it_is_temporary():
    reasons = evaluate_qualification(
        rules("Degree of a recognised University or Equivalent."),
        student(TENTH, Step(level=Level.GRADUATION, marks=64.0, is_completed=False)),
    )
    blocking = [r for r in reasons if r.blocks_application]
    assert blocking
    assert "once you have" in blocking[0].text
    assert blocking[0].is_permanent is False


def test_a_tenth_pass_qualifies_for_a_tenth_level_exam():
    reasons = evaluate_qualification(
        rules("10th standard pass with Mathematics and English"), student(TENTH)
    )
    assert [r for r in reasons if r.blocks_application] == []


def test_marks_are_read_from_the_level_the_exam_asks_about():
    reasons = evaluate_qualification(
        rules("Degree of a recognised University", minimum=60.0),
        student(
            TENTH,
            Step(
                level=Level.GRADUATION, marks=5.5, marks_kind=MarksKind.CGPA,
                cgpa_scale=10, is_completed=True,
            ),
        ),
    )
    blocking = [r for r in reasons if r.blocks_application]
    assert blocking
    assert "55%" in blocking[0].text
    assert "graduation" in blocking[0].text


def test_an_unreadable_requirement_says_so_instead_of_guessing():
    reasons = evaluate_qualification(rules("As per the rules of the department"), student(TENTH))
    assert any("read the notification yourself" in r.text for r in reasons)


def test_a_desirable_qualification_never_blocks():
    exam = ExamRules(
        exam_name="Test", source_id="upsc", document_sha256="x",
        qualifications=[
            Qualification(
                requirement="Diploma in Company Law or Labour Laws",
                citation=Citation(
                    page=3,
                    quote="DESIRABLE QUALIFICATIONS: Diploma in Company Law/Labour Laws.",
                ),
            )
        ],
    )
    reasons = evaluate_qualification(exam, student(TENTH))
    assert [r for r in reasons if r.blocks_application] == []
    assert any("desirable, not required" in r.text for r in reasons)


def test_an_essential_qualification_still_blocks():
    exam = ExamRules(
        exam_name="Test", source_id="upsc", document_sha256="x",
        qualifications=[
            Qualification(
                requirement="Degree of a recognised University",
                citation=Citation(
                    page=3, quote="ESSENTIAL QUALIFICATIONS: EDUCATIONAL Degree of a recognised University."
                ),
            )
        ],
    )
    assert [r for r in evaluate_qualification(exam, student(TENTH)) if r.blocks_application]


def test_preferable_wording_is_also_treated_as_optional():
    exam = ExamRules(
        exam_name="Test", source_id="upsc", document_sha256="x",
        qualifications=[
            Qualification(
                requirement="Degree in law",
                citation=Citation(page=4, quote="A degree in law is preferable but not essential."),
            )
        ],
    )
    assert [r for r in evaluate_qualification(exam, student(TENTH)) if r.blocks_application] == []
