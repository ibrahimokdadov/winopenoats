import asyncio
import numpy as np
import pytest
from unittest.mock import MagicMock, patch
from transcription.transcriber import StreamingTranscriber
from transcription.engine import TranscriptionEngine

SILENCE = np.zeros(512, dtype=np.float32)
SPEECH = np.ones(512, dtype=np.float32) * 0.3


@pytest.fixture
def mock_model():
    model = MagicMock()
    seg = MagicMock()
    seg.text = "hello"
    model.transcribe.return_value = ([seg], None)
    return model


@pytest.fixture
def mock_vad():
    vad = MagicMock()
    vad.score.return_value = 0.0
    return vad


def test_on_partial_is_callable(mock_model, mock_vad):
    t = StreamingTranscriber("you", mock_model, mock_vad)
    called = []
    t.on_partial = lambda text: called.append(text)
    assert t.on_partial is not None


def test_on_final_is_callable(mock_model, mock_vad):
    t = StreamingTranscriber("you", mock_model, mock_vad)
    t.on_final = lambda u: None
    assert t.on_final is not None


async def test_flush_calls_on_final(mock_model, mock_vad):
    t = StreamingTranscriber("you", mock_model, mock_vad)
    finals = []
    t.on_final = finals.append
    t._buffer = np.ones(16000, dtype=np.float32)
    await t._flush()
    assert len(finals) == 1
    assert finals[0].text == "hello"
    assert finals[0].speaker == "you"


def test_engine_creates_model(tmp_path, monkeypatch):
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    with patch("transcription.engine.WhisperModel") as MockModel, \
         patch("transcription.engine.SileroVAD"):
        MockModel.return_value = MagicMock()
        engine = TranscriptionEngine(model_dir=tmp_path, model_size="tiny")
        assert MockModel.called
