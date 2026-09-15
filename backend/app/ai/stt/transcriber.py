"""AI 골프 일기(Phase 6)용 STT.

OpenAI Whisper API 같은 과금 API 대신, RAG의 임베딩 모델(app/ai/rag/embeddings.py)과 같은
원칙으로 로컬 faster-whisper(CTranslate2 기반, PyTorch 불필요)를 API 키 없이 그대로 쓴다.
라이브 데모 계정에서도 실제 녹음을 과금 걱정 없이 받을 수 있게 하기 위함이다.

원본 오디오는 전사 직후 폐기한다 — 서버에 영구 저장하지 않는다.
"""
import tempfile
from functools import lru_cache
from pathlib import Path

from faster_whisper import WhisperModel

from app.core.config import get_settings


class SttTranscriptionError(Exception):
    """오디오를 디코딩/전사하지 못했을 때 (지원하지 않는 형식, 손상된 파일 등)."""


@lru_cache
def get_stt_model() -> WhisperModel:
    settings = get_settings()
    return WhisperModel(settings.whisper_model_size, device="cpu", compute_type="int8")


def transcribe_audio(audio_bytes: bytes, filename: str | None = None) -> str:
    suffix = Path(filename).suffix if filename else ".webm"
    model = get_stt_model()

    with tempfile.NamedTemporaryFile(suffix=suffix) as tmp:
        tmp.write(audio_bytes)
        tmp.flush()
        try:
            # vad_filter: Silero VAD로 무음/잡음 구간을 먼저 걸러내고 음성 구간만 전사한다.
            # 마이크에서 떨어져 말해 배경 잡음이 섞여도 없는 말을 지어내는 오인식이 줄어든다.
            segments, _ = model.transcribe(tmp.name, language="ko", vad_filter=True)
            text = "".join(segment.text for segment in segments).strip()
        except Exception as exc:  # faster-whisper는 디코딩 실패 시 다양한 예외를 던진다
            raise SttTranscriptionError("음성을 인식하지 못했습니다.") from exc

    if not text:
        raise SttTranscriptionError("음성에서 내용을 인식하지 못했습니다.")
    return text
