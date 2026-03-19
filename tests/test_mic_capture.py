import asyncio
import numpy as np
import pytest
from audio.mic_capture import MicCapture


@pytest.fixture
def loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


def test_rms_initial(loop):
    cap = MicCapture(loop)
    assert cap.rms == 0.0


def test_rms_updates_on_callback(loop):
    cap = MicCapture(loop)
    chunk = np.ones((512, 1), dtype=np.float32) * 0.5
    cap._callback(chunk, 512, None, None)
    assert cap.rms > 0.0


def test_callback_puts_to_queue(loop):
    cap = MicCapture(loop)
    chunk = np.ones((512, 1), dtype=np.float32)
    cap._callback(chunk, 512, None, None)
    loop.run_until_complete(asyncio.sleep(0))
    assert not cap._queue.empty()


def test_available_default(loop):
    cap = MicCapture(loop)
    assert cap.available is True
