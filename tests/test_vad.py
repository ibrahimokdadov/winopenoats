import numpy as np
import pytest
from transcription.vad import SileroVAD


@pytest.fixture(scope="module")
def vad():
    return SileroVAD()


def test_returns_float(vad):
    chunk = np.zeros(512, dtype=np.float32)
    score = vad.score(chunk)
    assert isinstance(score, float)
    assert 0.0 <= score <= 1.0


def test_silence_low_score(vad):
    silence = np.zeros(512, dtype=np.float32)
    score = vad.score(silence)
    assert score < 0.5


def test_reset_clears_state(vad):
    vad.reset()  # should not raise
