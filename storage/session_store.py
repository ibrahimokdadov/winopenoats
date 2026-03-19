import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4, UUID
from models.models import Utterance, Suggestion, SessionIndex


class SessionStore:
    def __init__(self, session_dir: Path, notes_dir: Path):
        self._session_dir = session_dir
        self._notes_dir = notes_dir
        self.session_id = str(uuid4())
        self._jsonl_path = session_dir / f"{self.session_id}.jsonl"
        self._file = open(self._jsonl_path, "a", encoding="utf-8")
        self._utterance_count = 0
        self._started_at = datetime.now(timezone.utc)

    def _write_line(self, obj: dict):
        self._file.write(json.dumps(obj) + "\n")
        self._file.flush()

    def write_utterance(self, u: Utterance):
        self._write_line({
            "type": "utterance",
            "id": str(u.id),
            "speaker": u.speaker,
            "text": u.text,
            "timestamp": u.timestamp.isoformat(),
        })
        self._utterance_count += 1

    def write_suggestion(self, s: Suggestion):
        self._write_line({
            "type": "suggestion",
            "id": str(s.id),
            "headline": s.headline,
            "coaching": s.coaching,
            "text": s.text,
            "trigger": {"kind": s.trigger.kind, "confidence": s.trigger.confidence},
            "evidence": [
                {
                    "text": e.text,
                    "source_file": e.source_file,
                    "header_context": e.header_context,
                    "relevance_score": e.relevance_score,
                }
                for e in s.evidence
            ],
            "decision": {
                "relevance": s.decision.relevance,
                "helpfulness": s.decision.helpfulness,
                "novelty": s.decision.novelty,
                "timing": s.decision.timing,
                "surfaced": s.decision.surfaced,
            },
            "feedback": s.feedback,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

    def finalize(self, title: str, template_id: str | None) -> SessionIndex:
        self.close()
        index = SessionIndex(
            id=UUID(self.session_id),
            timestamp=self._started_at,
            utterance_count=self._utterance_count,
            title=title,
        )
        index_path = self._session_dir / f"{self.session_id}.index.json"
        index_path.write_text(json.dumps({
            "id": self.session_id,
            "timestamp": self._started_at.isoformat(),
            "utterance_count": self._utterance_count,
            "title": title,
        }))
        sidecar_path = self._session_dir / f"{self.session_id}.sidecar.json"
        sidecar_path.write_text(json.dumps({
            "session_id": self.session_id,
            "notes_file": f"notes/{self.session_id}.md",
            "template_id": template_id,
        }))
        return index

    def close(self):
        if self._file and not self._file.closed:
            self._file.close()
