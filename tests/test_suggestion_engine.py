from datetime import datetime, timezone, timedelta
import pytest
from models.models import Utterance
from intelligence.suggestion_engine import detect_trigger, pre_filter


def make_utterance(text, speaker="them"):
    return Utterance(speaker=speaker, text=text, timestamp=datetime.now(timezone.utc))


def test_detect_trigger_question():
    u = make_utterance("What is the pricing for enterprise customers?")
    trigger = detect_trigger(u)
    assert trigger is not None
    assert trigger.kind == "explicit_question"


def test_detect_trigger_decision():
    # No "?" so question pattern won't fire first; "should we" fires decision_point
    u = make_utterance("I think we should go with option A over option B")
    trigger = detect_trigger(u)
    assert trigger is not None
    assert trigger.kind == "decision_point"


def test_detect_trigger_none():
    u = make_utterance("Ok thanks")
    trigger = detect_trigger(u)
    assert trigger is None


def test_pre_filter_too_short():
    u = make_utterance("Ok?")
    assert pre_filter(u, last_suggestion_time=None) is False


def test_pre_filter_passes():
    u = make_utterance("What are our retention metrics for this quarter?")
    assert pre_filter(u, last_suggestion_time=None) is True


def test_cooldown_blocks():
    u = make_utterance("What is the pricing for enterprise customers?")
    recent = datetime.now(timezone.utc) - timedelta(seconds=30)
    assert pre_filter(u, last_suggestion_time=recent) is False
