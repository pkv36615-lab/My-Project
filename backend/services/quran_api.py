from __future__ import annotations

from dataclasses import dataclass
import requests


@dataclass(frozen=True)
class AyahData:
    surah: int
    ayah: int
    text: str
    audio_url: str


def fetch_ayah_text(surah: int, ayah: int) -> str:
    response = requests.get(
        f"https://api.alquran.cloud/v1/ayah/{surah}:{ayah}/quran-uthmani",
        timeout=30,
    )
    response.raise_for_status()
    payload = response.json()
    return payload["data"]["text"]


def build_audio_url(base_url: str, surah: int, ayah: int) -> str:
    key = f"{surah:03d}{ayah:03d}"
    return f"{base_url}/{key}.mp3"


def fetch_ayah_data(surah: int, ayah: int, audio_base_url: str) -> AyahData:
    text = fetch_ayah_text(surah, ayah)
    audio_url = build_audio_url(audio_base_url, surah, ayah)
    return AyahData(surah=surah, ayah=ayah, text=text, audio_url=audio_url)
