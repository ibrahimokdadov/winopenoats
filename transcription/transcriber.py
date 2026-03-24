import asyncio
import numpy as np
from datetime import datetime, timezone
from typing import AsyncIterator, Callable, Literal
from models.models import Utterance
from transcription.vad import SileroVAD, FRAME_SAMPLES, THRESHOLD

FLUSH_SAMPLES = 16000 * 6       # 6 seconds of speech max
SILENCE_SAMPLES = 16000         # 1s silence triggers flush (longer = more context)
MIN_SAMPLES = 8000               # minimum before eligible to flush
PREROLL_SAMPLES = 16000 // 2    # 500ms preroll for word boundary context


class StreamingTranscriber:
    def __init__(
        self,
        speaker: Literal["you", "them"],
        model,
        vad: SileroVAD,
    ):
        self._speaker = speaker
        self._model = model
        self._vad = vad
        self._buffer = np.array([], dtype=np.float32)
        self._preroll = np.array([], dtype=np.float32)
        self._silence_count = 0
        self._in_speech = False

        # Plain synchronous callables — must not be async def
        self.on_partial: Callable[[str], None] = lambda text: None
        self.on_final: Callable[[Utterance], None] = lambda u: None

    async def process(self, audio_stream: AsyncIterator[np.ndarray]) -> None:
        async for chunk in audio_stream:
            await self._handle_chunk(chunk)

    async def _handle_chunk(self, chunk: np.ndarray) -> None:
        self._preroll = np.concatenate([self._preroll, chunk])[-PREROLL_SAMPLES:]

        for i in range(0, len(chunk) - FRAME_SAMPLES + 1, FRAME_SAMPLES):
            frame = chunk[i: i + FRAME_SAMPLES]
            prob = self._vad.score(frame)
            is_speech = prob >= THRESHOLD

            if is_speech:
                if not self._in_speech:
                    self._in_speech = True
                    self._buffer = self._preroll.copy()
                self._buffer = np.concatenate([self._buffer, frame])
                self._silence_count = 0

                if len(self._buffer) >= FLUSH_SAMPLES:
                    await self._flush()
            else:
                if self._in_speech:
                    self._buffer = np.concatenate([self._buffer, frame])
                    self._silence_count += FRAME_SAMPLES
                    if self._silence_count >= SILENCE_SAMPLES:
                        await self._flush()

    async def _flush(self) -> None:
        if len(self._buffer) < MIN_SAMPLES:
            return
        buf = self._buffer.copy()
        self._buffer = np.array([], dtype=np.float32)
        self._silence_count = 0
        self._in_speech = False
        self._vad.reset()

        self.on_partial("...")

        segments, _ = self._model.transcribe(
            buf,
            language="en",
            beam_size=5,
        )
        text = " ".join(s.text for s in segments).strip()
        if text:
            utterance = Utterance(
                speaker=self._speaker,
                text=text,
                timestamp=datetime.now(timezone.utc),
            )
            self.on_final(utterance)
