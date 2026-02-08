from __future__ import annotations

import random
from pathlib import Path

from moviepy.editor import (  # type: ignore
    AudioFileClip,
    ColorClip,
    CompositeVideoClip,
    TextClip,
    VideoFileClip,
)

from backend.config import (
    BACKGROUND_VIDEOS_DIR,
    FALLBACK_BG_COLOR,
    FONT_COLOR,
    FONT_FAMILY,
    TEXT_MARGIN,
)


def _pick_background(duration: float, size: tuple[int, int]) -> VideoFileClip | ColorClip:
    candidates = list(BACKGROUND_VIDEOS_DIR.glob("*.mp4"))
    if candidates:
        clip = VideoFileClip(str(random.choice(candidates)))
        if clip.duration < duration:
            clip = clip.loop(duration=duration)
        return clip.subclip(0, duration).resize(size)
    return ColorClip(size=size, color=FALLBACK_BG_COLOR, duration=duration)


def _render_text(text: str, duration: float, size: tuple[int, int]) -> TextClip:
    return TextClip(
        text,
        font=FONT_FAMILY,
        fontsize=70,
        color=FONT_COLOR,
        method="caption",
        align="center",
        size=(size[0] - TEXT_MARGIN * 2, None),
    ).set_duration(duration)


def compose_video(
    text: str,
    audio_path: Path,
    output_path: Path,
    duration: float,
    size: tuple[int, int],
    fps: int,
    threads: int,
    preset: str,
) -> Path:
    background = _pick_background(duration, size)
    text_clip = _render_text(text, duration, size).set_position(("center", "center"))
    glow = _render_text(text, duration, size).margin(
        left=10, right=10, top=10, bottom=10, opacity=0
    ).set_opacity(0.1).set_position(("center", "center"))
    audio = AudioFileClip(str(audio_path))

    composite = CompositeVideoClip([background, glow, text_clip], size=size)
    composite = composite.set_audio(audio).set_duration(duration)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    composite.write_videofile(
        str(output_path),
        fps=fps,
        codec="libx264",
        audio_codec="aac",
        threads=threads,
        preset=preset,
    )
    return output_path
