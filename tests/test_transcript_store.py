import pytest
from datetime import datetime, timezone
from models.models import Utterance, ConversationState
from storage.transcript_store import TranscriptStore


@pytest.fixture
def store(qapp):
    return TranscriptStore()


def test_append_emits_signal(store, qtbot):
    u = Utterance(speaker="you", text="hello", timestamp=datetime.now(timezone.utc))
    with qtbot.waitSignal(store.utterance_added, timeout=1000) as blocker:
        store.append(u)
    assert blocker.args[0].text == "hello"


def test_clear_resets(store):
    u = Utterance(speaker="you", text="hello", timestamp=datetime.now(timezone.utc))
    store.append(u)
    store.clear()
    assert store.utterances == []


def test_update_partial(store, qtbot):
    with qtbot.waitSignal(store.partial_updated, timeout=1000) as blocker:
        store.update_partial("you", "hel...")
    assert blocker.args == ["you", "hel..."]


def test_recent_utterances(store):
    for i in range(15):
        store.append(Utterance(speaker="you", text=f"msg {i}", timestamp=datetime.now(timezone.utc)))
    assert len(store.recent_utterances) == 10
