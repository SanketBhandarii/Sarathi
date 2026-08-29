from __future__ import annotations

from datetime import date
from pathlib import Path

from app.db.base import session_scope
from app.delivery.messenger import ConsoleMessenger, OutgoingMessage
from app.journal.runner import run_nightly_check
from app.language.phrases import Language, say


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


def test_a_quiet_day_sends_nothing_to_the_student():
    recorder = RecordingMessenger()
    with session_scope() as session:
        run_nightly_check(
            session, student_id=1, today=date(2026, 7, 15),
            messenger=recorder, send_to="+910000000000",
        )
    assert recorder.sent == []


def test_a_deadline_day_actually_delivers():
    recorder = RecordingMessenger()
    with session_scope() as session:
        run = run_nightly_check(
            session, student_id=1, today=date(2026, 8, 29),
            messenger=recorder, send_to="+910000000000",
        )
    assert run.messages_sent >= 1
    assert len(recorder.sent) == run.messages_sent


def test_nothing_is_delivered_when_no_number_is_given():
    recorder = RecordingMessenger()
    with session_scope() as session:
        run_nightly_check(session, student_id=1, today=date(2026, 8, 29), messenger=recorder)
    assert recorder.sent == []


def test_a_message_can_go_out_in_hindi():
    recorder = RecordingMessenger()
    with session_scope() as session:
        run_nightly_check(
            session, student_id=1, today=date(2026, 8, 29),
            messenger=recorder, send_to="+910000000000", language=Language.HINDI,
        )
    assert all(m.language is Language.HINDI for m in recorder.sent)


def test_deadline_wording_exists_in_hindi():
    text = say("deadline.days_left", Language.HINDI, exam="X", days=13, when="11 September")
    assert "13" in text
    assert any("\u0900" <= ch <= "\u097f" for ch in text)
