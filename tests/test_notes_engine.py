import pytest
from datetime import datetime, timezone
from models.models import Utterance
from intelligence.notes_engine import NotesEngine, format_transcript


def make_utterance(speaker, text):
    return Utterance(speaker=speaker, text=text, timestamp=datetime.now(timezone.utc))


def test_format_transcript_basic():
    utterances = [make_utterance("you", "Hello"), make_utterance("them", "Hi")]
    result = format_transcript(utterances)
    assert "You:" in result
    assert "Them:" in result


def test_format_transcript_truncates():
    big = [make_utterance("you", "x" * 1000) for _ in range(100)]
    result = format_transcript(big)
    assert len(result) <= 65000


async def test_generate_calls_llm():
    engine = NotesEngine(llm_complete=None, system_prompt="Summarize this meeting.")
    chunks = []
    engine.on_chunk = chunks.append

    async def fake_llm(messages, stream=False):
        return "## Summary\nGreat meeting."

    engine._llm = fake_llm
    utterances = [make_utterance("you", "We discussed pricing.")]
    result = await engine.generate(utterances)
    assert "Summary" in result


def test_is_generating_flag():
    engine = NotesEngine(llm_complete=None, system_prompt="")
    assert engine.is_generating is False
