import asyncio
import numpy as np
from typing import AsyncIterator

try:
    import pyaudiowpatch as pyaudio
    _PA_AVAILABLE = True
except (ImportError, OSError):
    _PA_AVAILABLE = False


class SystemCapture:
    TARGET_RATE = 16000
    CHUNK_FRAMES = 512  # at TARGET_RATE (32 ms)

    def __init__(self, loop: asyncio.AbstractEventLoop):
        self._loop = loop
        self._queue: asyncio.Queue[np.ndarray] = asyncio.Queue(maxsize=50)
        self._pa = None
        self._stream = None
        self.rms: float = 0.0
        self.available: bool = True
        self._native_rate: int = self.TARGET_RATE
        self._native_channels: int = 1

    def _on_chunk(self, chunk: np.ndarray):
        # Mix to mono
        if chunk.ndim > 1:
            chunk = chunk.mean(axis=1)
        # Resample to TARGET_RATE if needed (anti-aliased)
        if self._native_rate != self.TARGET_RATE:
            try:
                from scipy.signal import resample_poly
                from math import gcd
                g = gcd(self.TARGET_RATE, self._native_rate)
                up, down = self.TARGET_RATE // g, self._native_rate // g
                chunk = resample_poly(chunk, up, down).astype(np.float32)
            except ImportError:
                ratio = self.TARGET_RATE / self._native_rate
                target_len = max(1, int(len(chunk) * ratio))
                indices = np.linspace(0, len(chunk) - 1, target_len)
                chunk = np.interp(indices, np.arange(len(chunk)), chunk).astype(np.float32)
        self.rms = float(np.sqrt(np.mean(chunk ** 2)))
        c = chunk.copy()
        def _put():
            try:
                self._queue.put_nowait(c)
            except asyncio.QueueFull:
                pass
        self._loop.call_soon_threadsafe(_put)

    def _pa_callback(self, in_data, frame_count, time_info, status):
        import pyaudiowpatch as pyaudio
        chunk = np.frombuffer(in_data, dtype=np.float32).reshape(-1, self._native_channels)
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
            self._native_rate = int(loopback["defaultSampleRate"])
            self._native_channels = int(loopback["maxInputChannels"])
            # Capture at native rate with proportional chunk size
            native_chunk = int(self.CHUNK_FRAMES * self._native_rate / self.TARGET_RATE)
            self._stream = self._pa.open(
                format=pyaudio.paFloat32,
                channels=self._native_channels,
                rate=self._native_rate,
                input=True,
                input_device_index=loopback["index"],
                frames_per_buffer=native_chunk,
                stream_callback=self._pa_callback,
            )
            self._stream.start_stream()
        except Exception as e:
            import logging
            logging.getLogger(__name__).error("SystemCapture.start failed: %s", e, exc_info=True)
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
