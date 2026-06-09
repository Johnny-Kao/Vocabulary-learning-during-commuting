#!/usr/bin/env python3
"""
Generate per-word TTS audio files from vocab.json.

FR: Thomas (Enhanced)  → assets/audio/fr/{id}.mp3
DE: Anna (Premium)     → assets/audio/de/{id}.mp3

Usage:
    python3 scripts/generate_vocab_audio.py --lang fr
    python3 scripts/generate_vocab_audio.py --lang de
    python3 scripts/generate_vocab_audio.py --lang all
    python3 scripts/generate_vocab_audio.py --lang fr --id A1-0001
    python3 scripts/generate_vocab_audio.py --lang fr --force
"""

import argparse
import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).parent.parent
VOCAB_JSON = ROOT / "vocab.json"
AUDIO_DIR  = ROOT / "assets" / "audio"

VOICES = {
    "fr": "Thomas (Enhanced)",  # Thomas Enhanced — macOS French voice
    "de": "Anna (Premium)",     # Anna Premium    — macOS German voice
}
RATE = 160  # words per minute; adjust if speech feels rushed


def generate_tts(text: str, output_mp3: Path, voice: str, force: bool = False) -> None:
    if output_mp3.exists() and not force:
        print(f"  skip  {output_mp3.relative_to(ROOT)}")
        return
    output_mp3.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.NamedTemporaryFile(suffix=".aiff", delete=False) as tmp:
        tmp_path = Path(tmp.name)
    try:
        subprocess.run(
            ["say", "-v", voice, "-r", str(RATE), "-o", str(tmp_path), text],
            check=True,
        )
        subprocess.run(
            ["ffmpeg", "-y", "-i", str(tmp_path),
             "-codec:a", "libmp3lame", "-q:a", "4", str(output_mp3)],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        print(f"  gen   {output_mp3.relative_to(ROOT)}")
    finally:
        tmp_path.unlink(missing_ok=True)


def process_lang(vocab: list[dict], lang: str, target_id: str | None, force: bool) -> None:
    voice = VOICES[lang]
    field = lang  # "fr" or "de" key in vocab entry
    out_dir = AUDIO_DIR / lang

    for entry in vocab:
        if target_id and entry["id"] != target_id:
            continue
        text = entry.get(field, "").strip()
        if not text:
            print(f"  WARN  {entry['id']}: empty {lang} field, skipping")
            continue
        mp3 = out_dir / f"{entry['id']}.mp3"
        generate_tts(text, mp3, voice, force=force)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate vocab TTS audio via macOS say")
    parser.add_argument("--lang", choices=["fr", "de", "all"], required=True,
                        help="Language to generate (fr / de / all)")
    parser.add_argument("--id", metavar="WORD_ID",
                        help="Process only this word ID, e.g. A1-0001")
    parser.add_argument("--force", action="store_true",
                        help="Overwrite existing files")
    args = parser.parse_args()

    with open(VOCAB_JSON, encoding="utf-8") as f:
        vocab = json.load(f)

    langs = ["fr", "de"] if args.lang == "all" else [args.lang]
    for lang in langs:
        print(f"\n── {lang.upper()} ({VOICES[lang]}) ──────────────────────────────")
        process_lang(vocab, lang, target_id=args.id, force=args.force)

    print("\nDone.")


if __name__ == "__main__":
    main()
