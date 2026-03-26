import asyncio
import numpy as np
from typing import AsyncIterator

try:
    import sounddevice as sd
    _SD_AVAILABLE = True
except ImportError:
    _SD_AVAILABLE = False


class MicCapture:
    SAMPLE_RATE = 16000
    CHUNK_FRAMES = 512

    def __init__(self, loop: asyncio.AbstractEventLoop, device=None):
        self._loop = loop
        self._device = device
        self._queue: asyncio.Queue[np.ndarray] = asyncio.Queue(maxsize=50)
        self._stream = None
        self.rms: float = 0.0
        self.available: bool = True
        self.muted: bool = False

    def _callback(self, indata: np.ndarray, frames: int, time, status):
        chunk = indata[:, 0].copy() if indata.ndim > 1 else indata.copy()
        if self.muted:
            self.rms = 0.0
            chunk = np.zeros_like(chunk)
        else:
            self.rms = float(np.sqrt(np.mean(chunk ** 2)))
        def _put():
            try:
                self._queue.put_nowait(chunk)
            except asyncio.QueueFull:
                pass
        self._loop.call_soon_threadsafe(_put)

    def start(self):
        if not _SD_AVAILABLE:
            self.available = False
            return
        try:
            self._stream = sd.InputStream(
                samplerate=self.SAMPLE_RATE,
                channels=1,
                dtype="float32",
                blocksize=self.CHUNK_FRAMES,
                device=self._device,
                callback=self._callback,
            )
            self._stream.start()
        except Exception as e:
            import logging
            logging.getLogger(__name__).error("MicCapture.start failed: %s", e, exc_info=True)
            self.available = False

    def stop(self):
        if self._stream:
            self._stream.stop()
            self._stream.close()
            self._stream = None

    async def stream(self) -> AsyncIterator[np.ndarray]:
        while True:
            yield await self._queue.get()
