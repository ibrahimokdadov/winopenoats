import numpy as np

FRAME_SAMPLES = 512  # 32ms at 16kHz
THRESHOLD = 0.5


class SileroVAD:
    def __init__(self):
        from silero_vad import load_silero_vad
        self._model = load_silero_vad()
        self._model.eval()

    def score(self, chunk: np.ndarray) -> float:
        """Return speech probability for a 512-sample float32 chunk at 16kHz."""
        import torch
        if len(chunk) != FRAME_SAMPLES:
            chunk = np.resize(chunk, FRAME_SAMPLES)
        tensor = torch.from_numpy(chunk.astype(np.float32))
        with torch.no_grad():
            return float(self._model(tensor, 16000).item())

    def reset(self):
        self._model.reset_states()
