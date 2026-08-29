from __future__ import annotations

from pathlib import Path

from app.extraction.schema import ExamRules


class ExamRulesStore:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, sha256: str) -> Path:
        return self.root / f"{sha256[:16]}.json"

    def get(self, sha256: str) -> ExamRules | None:
        path = self._path(sha256)
        if not path.exists():
            return None
        return ExamRules.model_validate_json(path.read_text("utf-8"))

    def put(self, rules: ExamRules) -> Path:
        path = self._path(rules.document_sha256)
        path.write_text(rules.model_dump_json(indent=2), encoding="utf-8")
        return path

    def all(self) -> list[ExamRules]:
        return [
            ExamRules.model_validate_json(p.read_text("utf-8"))
            for p in sorted(self.root.glob("*.json"))
        ]
