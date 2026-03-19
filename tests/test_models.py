from datetime import datetime, timezone
from uuid import UUID, uuid4
from models.models import (
    Utterance, ConversationState, SuggestionTrigger,
    SuggestionEvidence, SuggestionDecision, Suggestion,
    SessionIndex, MeetingTemplate,
)


def test_utterance_defaults():
    u = Utterance(speaker="you", text="hello", timestamp=datetime.now(timezone.utc))
    assert isinstance(u.id, UUID)
    assert u.speaker == "you"


def test_suggestion_trigger_kinds():
    t = SuggestionTrigger(kind="explicit_question", confidence=0.9)
    assert t.confidence == 0.9


def test_suggestion_evidence():
    e = SuggestionEvidence(text="content", source_file="f.md", header_context="# H", relevance_score=0.8)
    assert e.relevance_score == 0.8


def test_suggestion_decision_surfaced():
    d = SuggestionDecision(relevance=0.8, helpfulness=0.7, novelty=0.6, timing=0.9, surfaced=True)
    assert d.surfaced is True


def test_full_suggestion():
    trigger = SuggestionTrigger(kind="decision_point", confidence=0.85)
    evidence = [SuggestionEvidence("txt", "f.md", "# H", 0.9)]
    decision = SuggestionDecision(0.8, 0.7, 0.6, 0.9, True)
    s = Suggestion(headline="h", coaching="c", text="t", trigger=trigger, evidence=evidence, decision=decision)
    assert s.feedback is None
    assert isinstance(s.id, UUID)


def test_conversation_state_defaults():
    cs = ConversationState()
    assert cs.topic == ""
    assert cs.open_questions == []


def test_session_index():
    si = SessionIndex(id=uuid4(), timestamp=datetime.now(timezone.utc), utterance_count=5, title="Meeting")
    assert si.utterance_count == 5


def test_meeting_template():
    mt = MeetingTemplate(name="Sales", system_prompt="You are...")
    assert isinstance(mt.id, UUID)
