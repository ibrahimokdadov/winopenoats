import asyncio
from typing import Callable
from models.models import Utterance

MAX_CHARS = 60000
KEEP_CHARS = 20000


def format_transcript(utterances: list[Utterance]) -> str:
    lines = []
    for u in utterances:
        speaker = "You" if u.speaker == "you" else "Them"
        ts = u.timestamp.strftime("%H:%M")
        lines.append(f"[{ts}] {speaker}: {u.text}")
    text = "\n".join(lines)
    if len(text) > MAX_CHARS:
        text = text[:KEEP_CHARS] + "\n\n[...middle truncated...]\n\n" + text[-KEEP_CHARS:]
    return text


class NotesEngine:
    def __init__(self, llm_complete, system_prompt: str):
        self._llm = llm_complete
        self._system_prompt = system_prompt
        self.is_generating: bool = False
        self.on_chunk: Callable[[str], None] = lambda c: None
        self._task: asyncio.Task | None = None

    async def generate(self, utterances: list[Utterance]) -> str:
        if self.is_generating:
            return ""
        self.is_generating = True
        transcript = format_transcript(utterances)
        messages = [
            {"role": "system", "content": self._system_prompt},
            {"role": "user", "content": transcript},
        ]
        try:
            result = await self._llm(messages)
            self.on_chunk(result)
            return result
        finally:
            self.is_generating = False

    def cancel(self):
        if self._task:
            self._task.cancel()
        self.is_generating = False
