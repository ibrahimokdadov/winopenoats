import asyncio
import numpy as np
from typing import AsyncIterator

try:
    import pyaudiowpatch as pyaudio
    _PA_AVAILABLE = True
except (ImportError, OSError):
    _PA_AVAILABLE = False


class SystemCapture:
    SAMPLE_RATE = 16000
    CHUNK_FRAMES = 512

    def __init__(self, loop: asyncio.AbstractEventLoop):
        self._loop = loop
        self._queue: asyncio.Queue[np.ndarray] = asyncio.Queue(maxsize=50)
        self._pa = None
        self._stream = None
        self.rms: float = 0.0
        self.available: bool = True

    def _on_chunk(self, chunk: np.ndarray):
        self.rms = float(np.sqrt(np.mean(chunk ** 2)))
        try:
            self._loop.call_soon_threadsafe(self._queue.put_nowait, chunk.copy())
        except asyncio.QueueFull:
            pass

    def _pa_callback(self, in_data, frame_count, time_info, status):
        import pyaudiowpatch as pyaudio
        chunk = np.frombuffer(in_data, dtype=np.float32)
        self._on_chunk(chunk)
        return (None, pyaudio.paContinue)

    def start(self):
        if not _PA_AVAILABLE:
            self.available = False
            return
        try:
            import pyaudiowpatch as pyaudio
            self._pa = pyaudio.PyAudio()
            loopback = self._pa.get_default_wasapi_loopback()
            self._stream = self._pa.open(
                format=pyaudio.paFloat32,
                channels=1,
                rate=self.SAMPLE_RATE,
                input=True,
                input_device_index=loopback["index"],
                frames_per_buffer=self.CHUNK_FRAMES,
                stream_callback=self._pa_callback,
            )
            self._stream.start_stream()
        except (OSError, Exception):
            self.available = False

    def stop(self):
        if self._stream:
            self._stream.stop_stream()
            self._stream.close()
        if self._pa:
            self._pa.terminate()

    async def stream(self) -> AsyncIterator[np.ndarray]:
        while True:
            yield await self._queue.get()
