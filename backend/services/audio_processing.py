from __future__ import annotations

from pathlib import Path
from typing import Tuple

import requests
from pydub import AudioSegment
from pydub.silence import detect_nonsilent

from backend.config import MAX_AUDIO_DURATION

def download_audio(url: str, output_path: Path) -> Path:
    response = requests.get(url, timeout=60)
    response.raise_for_status()
    output_path.write_bytes(response.content)
    return output_path


def trim_silence(audio: AudioSegment, silence_thresh: int = -50, padding_ms: int = 150) -> AudioSegment:
    nonsilent = detect_nonsilent(audio, min_silence_len=200, silence_thresh=silence_thresh)
    if not nonsilent:
        return audio
    start = max(nonsilent[0][0] - padding_ms, 0)
    end = min(nonsilent[-1][1] + padding_ms, len(audio))
    return audio[start:end]


def prepare_audio(url: str, output_path: Path) -> Tuple[Path, float]:
    download_audio(url, output_path)
    audio = AudioSegment.from_file(output_path)
    trimmed = trim_silence(audio)
    max_ms = MAX_AUDIO_DURATION * 1000
    if len(trimmed) > max_ms:
        trimmed = trimmed[:max_ms]
    trimmed.export(output_path, format="mp3")
    duration = trimmed.duration_seconds
    return output_path, duration
