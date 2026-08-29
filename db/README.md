# Database

Postgres. Seven tables, created by the migrations in `backend/migrations`.

| table | holds |
| --- | --- |
| students | one profile per student |
| source_documents | every notification pdf we have downloaded |
| exam_rules | the rules read out of each document, with citations |
| calendar_exams | exams announced in a commission calendar but not yet notified |
| journal_runs | one row per nightly run of the agent |
| journal_events | what the agent looked at during a run |
| deadlines | the dates a student must not miss |

Extracted rules are stored as JSONB. They are read and written as whole
documents, never queried field by field, and keeping them as one object means
the shape can change without a migration.

To apply migrations:

    cd backend
    .venv/Scripts/python -m alembic upgrade head
