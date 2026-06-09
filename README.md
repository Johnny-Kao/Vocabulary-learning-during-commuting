# Vocabulary Learning During Commuting

A mobile-first, offline-capable flashcard app for learning French and German vocabulary — designed to be used hands-free during a commute.

**Live:** [fr-voc.johnnykao.com](https://fr-voc.johnnykao.com) · [de-voc.johnnykao.com](https://de-voc.johnnykao.com)

---

## What it does

- 988 A1-level vocabulary words across 7 sections and 90 categories
- Every card shows 中文, English, and the target language simultaneously — no recall/blur mode
- Native TTS audio (macOS `say` → MP3) for French and German
- Progress saved per language in `localStorage`
- Quiz mode with confetti on correct answers
- Works on iPhone Safari (audio via persistent DOM `<audio>` element)
- Switching between `fr-voc.johnnykao.com` and `de-voc.johnnykao.com` auto-selects the language

---

## Workflow

### 1. Edit vocabulary

All source data lives in:

```
a1_vocab_master_988_final_tts_semantic_confirmed.csv
```

Columns used: `編號`, `大分類`, `小分類`, `分類內序號`, `中文_簡體`, `English`, `Français`, `Deutsch`

### 2. Generate `vocab.json`

```bash
python3 scripts/generate_vocab_json.py
```

Reads the CSV and writes `vocab.json` with all word entries, category metadata, and audio paths.

### 3. Generate TTS audio

Requires macOS (uses the built-in `say` command) and `ffmpeg`.

```bash
# French only
python3 scripts/generate_vocab_audio.py --lang fr

# German only
python3 scripts/generate_vocab_audio.py --lang de

# Both languages
python3 scripts/generate_vocab_audio.py --lang all

# Regenerate a single word
python3 scripts/generate_vocab_audio.py --lang fr --id A1-0042

# Force overwrite existing files
python3 scripts/generate_vocab_audio.py --lang fr --force
```

Voices used:
- French → `Thomas (Enhanced)`
- German → `Anna (Premium)`

Output: `assets/audio/fr/*.mp3` and `assets/audio/de/*.mp3`

### 4. Run locally

```bash
python3 -m http.server 8765
```

Open `http://localhost:8765/vocab_app_v9.html?lang=fr` or `?lang=de`.

> The app fetches `vocab.json` at runtime, so it must be served over HTTP — opening the HTML file directly won't work.

---

## Project structure

```
├── vocab_app_v9.html           # Main app (single-file, no build step)
├── index.html                  # Entry point → redirects to vocab_app_v9.html
├── vocab.json                  # Generated vocabulary data (988 entries)
├── assets/
│   └── audio/
│       ├── fr/                 # French MP3s (A1-0001.mp3 … A1-0988.mp3)
│       └── de/                 # German MP3s
├── scripts/
│   ├── generate_vocab_json.py  # CSV → vocab.json
│   └── generate_vocab_audio.py # vocab.json → TTS MP3s
└── a1_vocab_master_988_final_tts_semantic_confirmed.csv
```

---

## Tech

- Pure HTML / CSS / JS — no framework, no build step
- macOS `say` + `ffmpeg` for TTS audio generation
- Deployed on Cloudflare Pages
- Custom domains auto-select language via subdomain detection (`fr-*` → French, `de-*` → German)
