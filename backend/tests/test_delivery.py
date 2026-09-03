from __future__ import annotations

from datetime import date
from pathlib import Path

from app.db.base import session_scope
from app.delivery.messenger import ConsoleMessenger, OutgoingMessage
from app.journal.runner import run_nightly_check
from app.language.phrases import Language, say

from tests.conftest import A_DAY_NEAR_A_DEADLINE, A_QUIET_DAY


class RecordingMessenger:
    channel = "test"

    def __init__(self) -> None:
        self.sent: list[OutgoingMessage] = []

    def send(self, message: OutgoingMessage):
        self.sent.append(message)
        from datetime import datetime, timezone

        from app.delivery.messenger import SentMessage

        return SentMessage(
            to=message.to, body=message.body, channel=self.channel,
            sent_at=datetime.now(timezone.utc),
        )


def test_console_messenger_writes_a_line(tmp_path: Path):
    log = tmp_path / "messages.log"
    messenger = ConsoleMessenger(log_path=log)
    messenger.send(OutgoingMessage(to="+910000000000", body="hello"))
    assert "hello" in log.read_text(encoding="utf-8")


def test_a_quiet_day_sends_nothing_to_the_student(student_id):
    recorder = RecordingMessenger()
    with session_scope() as session:
        run_nightly_check(
            session, student_id=student_id, today=A_QUIET_DAY,
            messenger=recorder, send_to="+910000000000",
        )
    assert recorder.sent == []


def test_a_deadline_day_actually_delivers(student_id):
    recorder = RecordingMessenger()
    with session_scope() as session:
        run = run_nightly_check(
            session, student_id=student_id, today=A_DAY_NEAR_A_DEADLINE,
            messenger=recorder, send_to="+910000000000",
        )
    assert run.messages_sent >= 1
    assert len(recorder.sent) == run.messages_sent


def test_it_writes_to_the_address_on_your_account_when_none_is_given(student_id):
    recorder = RecordingMessenger()
    with session_scope() as session:
        run = run_nightly_check(
            session, student_id=student_id, today=A_DAY_NEAR_A_DEADLINE, messenger=recorder
        )
    assert run.messages_sent >= 1
    assert len(recorder.sent) == run.messages_sent
    assert all("@" in message.to for message in recorder.sent)


def test_a_student_with_no_account_is_not_written_to(student_with_no_account):
    recorder = RecordingMessenger()
    with session_scope() as session:
        run = run_nightly_check(
            session, student_id=student_with_no_account, today=A_DAY_NEAR_A_DEADLINE,
            messenger=recorder,
        )
    assert recorder.sent == []
    assert run.messages_sent == 0


def test_a_message_can_go_out_in_hindi(student_id):
    recorder = RecordingMessenger()
    with session_scope() as session:
        run_nightly_check(
            session, student_id=student_id, today=A_DAY_NEAR_A_DEADLINE,
            messenger=recorder, send_to="+910000000000", language=Language.HINDI,
        )
    assert all(m.language is Language.HINDI for m in recorder.sent)


def test_deadline_wording_exists_in_hindi():
    text = say("deadline.days_left", Language.HINDI, exam="X", days=13, when="11 September")
    assert "13" in text
    assert any("\u0900" <= ch <= "\u097f" for ch in text)
