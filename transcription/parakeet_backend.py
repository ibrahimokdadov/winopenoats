"""
Parakeet backend wrapping NVIDIA NeMo ASR models.
Exposes the same .transcribe(audio, **kwargs) interface as faster-whisper's WhisperModel
so StreamingTranscriber works unchanged.

Install: pip install nemo_toolkit[asr]
"""
import logging
import os
import tempfile

import numpy as np

logger = logging.getLogger(__name__)

_NEMO_AVAILABLE = False
try:
    import nemo.collections.asr as nemo_asr  # noqa: F401
    _NEMO_AVAILABLE = True
except ImportError:
    pass


class _Segment:
    """Minimal segment object matching faster-whisper's NamedTuple interface."""
    def __init__(self, text: str):
        self.text = text


class ParakeetModel:
    """
    Wraps a NeMo ASRModel to look like a faster-whisper WhisperModel.

    Usage:
        model = ParakeetModel("nvidia/parakeet-tdt-0.6b-v2")
        segments, _ = model.transcribe(audio_float32_16khz)
        text = " ".join(s.text for s in segments)
    """

    # Map our internal model IDs → HuggingFace pretrained names
    _HF_NAMES = {
        "parakeet-tdt-0.6b-v2": "nvidia/parakeet-tdt-0.6b-v2",
        "parakeet-tdt-1.1b":    "nvidia/parakeet-tdt-1.1b",
    }

    def __init__(self, model_id: str):
        if not _NEMO_AVAILABLE:
            raise RuntimeError(
                "NeMo is not installed.\n"
                "Run: pip install nemo_toolkit[asr]\n"
                "Then restart the app."
            )
        import nemo.collections.asr as nemo_asr
        hf_name = self._HF_NAMES.get(model_id, f"nvidia/{model_id}")
        logger.info("Loading Parakeet model %s …", hf_name)
        self._model = nemo_asr.models.ASRModel.from_pretrained(hf_name)
        self._model.eval()
        logger.info("Parakeet model ready.")

    def transcribe(self, audio: np.ndarray, **kwargs):
        """
        Transcribe a float32 16 kHz numpy array.
        Returns (list[_Segment], None) — same shape as faster-whisper.
        """
        import soundfile as sf

        # Write to a temp WAV; NeMo's transcribe() accepts file paths reliably
        fd, path = tempfile.mkstemp(suffix=".wav")
        try:
            os.close(fd)
            sf.write(path, audio, 16000, subtype="PCM_16")
            results = self._model.transcribe([path], batch_size=1)
        finally:
            try:
                os.unlink(path)
            except OSError:
                pass

        text = results[0] if results else ""
        if isinstance(text, list):   # some NeMo versions return nested lists
            text = text[0] if text else ""
        return [_Segment(str(text))], None
