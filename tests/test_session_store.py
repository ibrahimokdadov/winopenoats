import json
from pathlib import Path
from datetime import datetime, timezone
import pytest
from models.models import Utterance, SessionIndex
from storage.session_store import SessionStore


@pytest.fixture
def store(tmp_path):
    return SessionStore(session_dir=tmp_path, notes_dir=tmp_path)


def test_write_utterance(store, tmp_path):
    u = Utterance(speaker="you", text="hello", timestamp=datetime.now(timezone.utc))
    store.write_utterance(u)
    store.close()
    jsonl = list(tmp_path.glob("*.jsonl"))[0]
    line = json.loads(jsonl.read_text().splitlines()[0])
    assert line["type"] == "utterance"
    assert line["text"] == "hello"


def test_finalize_writes_index(store, tmp_path):
    u = Utterance(speaker="them", text="world", timestamp=datetime.now(timezone.utc))
    store.write_utterance(u)
    index = store.finalize(title="Test Meeting", template_id=None)
    assert isinstance(index, SessionIndex)
    assert index.utterance_count == 1
    assert (tmp_path / f"{store.session_id}.index.json").exists()
    assert (tmp_path / f"{store.session_id}.sidecar.json").exists()
