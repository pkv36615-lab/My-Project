from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


@dataclass(frozen=True)
class Reciter:
    id: str
    name: str
    audio_base_url: str


RECITERS: list[Reciter] = [
    Reciter("alafasy", "Mishary Rashid Alafasy", "https://everyayah.com/data/Alafasy_128kbps"),
    Reciter("husary", "Mahmoud Khalil Al-Husary", "https://everyayah.com/data/Husary_128kbps"),
    Reciter("sudais", "Abdurrahman Al-Sudais", "https://everyayah.com/data/Abdurrahmaan_As-Sudais_128kbps"),
    Reciter("shuraim", "Saud Al-Shuraim", "https://everyayah.com/data/Saood_ash-Shuraym_128kbps"),
    Reciter("ajamy", "Ahmed Al-Ajamy", "https://everyayah.com/data/Ahmed_ibn_Ali_al-Ajamy_128kbps"),
    Reciter("abdulbasit", "Abdul Basit Abdul Samad", "https://everyayah.com/data/Abdul_Basit_Mujawwad_128kbps"),
    Reciter("minshawi", "Muhammad Siddiq Al-Minshawi", "https://everyayah.com/data/Minshawy_Mujawwad_128kbps"),
    Reciter("tablawy", "Mohamed Mahmoud Tablawy", "https://everyayah.com/data/Mohammad_al_Tablaway_128kbps"),
    Reciter("shatri", "Abu Bakr Al-Shatri", "https://everyayah.com/data/Abu_Bakr_Ash-Shaatree_128kbps"),
    Reciter("ghamdi", "Saad Al-Ghamdi", "https://everyayah.com/data/Ghamadi_40kbps"),
]

BACKGROUND_VIDEOS_DIR = Path("assets/backgrounds")
FALLBACK_BG_COLOR = (7, 16, 34)

QUALITY_PRESETS = {
    "potato": {"size": (720, 1280), "fps": 24, "threads": 2, "preset": "fast"},
    "balanced": {"size": (1080, 1920), "fps": 30, "threads": 4, "preset": "medium"},
}
DEFAULT_QUALITY = "balanced"
MAX_AUDIO_DURATION = 600
FONT_FAMILY = "Amiri-Bold"
FONT_COLOR = "#F8F6F1"
HIGHLIGHT_COLOR = "#F4D06F"
TEXT_MARGIN = 120
