import asyncio
import numpy as np
import pytest
from unittest.mock import patch
from audio.system_capture import SystemCapture


@pytest.fixture
def loop():
    return asyncio.new_event_loop()


def test_available_false_when_pyaudio_missing(loop):
    with patch.dict("sys.modules", {"pyaudiowpatch": None}):
        cap = SystemCapture(loop)
        cap.start()
        assert cap.available is False


def test_rms_initial(loop):
    cap = SystemCapture(loop)
    assert cap.rms == 0.0


def test_callback_queues_chunk(loop):
    cap = SystemCapture(loop)
    chunk = np.ones(512, dtype=np.float32)
    cap._on_chunk(chunk)
    loop.run_until_complete(asyncio.sleep(0))
    assert not cap._queue.empty()
