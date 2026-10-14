# The pipeline scripts

`new-project.py` copies these into a project's `scripts/`; run them from the project root. They read
and write project files in the working directory (`SCRIPT.md`, `beats.json`, `asr-words.json`,
`vo-alignment.json`, `syl-times.json`, `parts/`, `index.html`, `ledger.json`).

## Voice first — the common case

```bash
python "<skill>/scripts/new-project.py" "<folder>" --name "Tên video" --voice "<recording>"
cd "<folder>"
python scripts/asr.py small              # -> asr-words.json
python scripts/plan-beats.py             # -> beats.json (scaffold for the aligner only)
python scripts/align-asr.py              # -> vo-alignment.json (real newA/newB per sentence)
python scripts/syl-times.py              # -> syl-times.json (every syllable)
python scripts/fix-syl.py                # starts inside a pause snap to the voice
python scripts/silences.py               # silent span of every sentence gap -> the cuts
python scripts/make-media.py             # the author's clips retimed + blurred, page stills
# ... author parts/ at the syllable times, set SC & co. in build.py ...
bash scripts/make.sh                     # build.py -> karaoke.py -> seam-stamp -> add-sfx.py
npm run check
```

## Voice last — the author records after seeing the picture

```bash
python scripts/asr.py small
python scripts/align-asr.py              # -> timing-map.json + vo-alignment.json
python scripts/install-map.py            # writes OLD[]/NEW[] into index.html, reads back
python scripts/recaption.py              # captions through the map
python scripts/resfx.py                  # SFX at mapped times
python scripts/audit-sync.py 0 110       # every cue vs the sentence playing then
```

## What each one is

| script | generic? | edit per project |
|---|---|---|
| `new-project.py` | **yes** | — run from the skill: template + scripts + assets into a new folder |
| `prep-voice.py` | **yes** | `--tempo` only when the author chooses a faster read |
| `asr.py` | mostly | `language="vi"`; model as argv (`small`, `medium`) |
| `plan-beats.py` | no | the `SCENES` table — sentence ranges per scene |
| `align-asr.py` | **yes** | — |
| `syl-times.py` | **yes** | — |
| `fix-syl.py` | **yes** | — |
| `silences.py` | **yes** | — optional times as argv print whether each sits in silence |
| `make-media.py` | engine yes | the `CLIPS` and `CROPS` lists (segments, crops, blur boxes) |
| `cdp.mjs` | **yes** | — `shot <url> <out.png> [--w --h --dpr --wait --js --clip --pad]`, `eval <url> <out.txt> --expr` |
| `build.py` | mostly | `SC` (cuts), `PROMPTS`, `CTA_WORD`, `STEPS`, `BRAND_LOGO`, `SLOGAN`, `CHAPTERS`, `PARTS` |
| `karaoke.py` | mostly | `SIDES`, `DARK`, `SKIP`; add `COMPOUNDS` for new two-syllable words |
| `add-sfx.py` | mostly | `RISER`, `LASER`, `CLICK`, `POP`, `BED`. Duration, voice end and swooshes are read from the files |
| `make.sh` | **yes** | — finds `motion-doctrine` in any parent `.claude/skills`, `~/.claude/skills`, or `$HF_SKILLS_DIR` |
| `sheet.py` | **yes** | — contact sheet of any video: `python scripts/sheet.py in.mp4 out.jpg 2.0` |
| `edit_helpers.py` | **yes** | — import it; see below |
| `install-map.py` | **yes** | — (voice-last only) |
| `recaption.py` | mostly | `HILITE`, `GAP`, `MAXW` (voice-last only) |
| `resfx.py` | no | the `CUES` list and `EC`; update on every retime (voice-last only) |
| `word-times.py` | no | the `QUERIES` list of phrases you want times for |
| `audit-sync.py` | **yes** | — |
| `synth-sfx.py` | **yes** | a synthesised palette, for pieces that do not use the house cues |
| `recaption-real.py` | **yes** | the older caption generator (one highlighted word); `karaoke.py` replaced it |

## Patching an index.html the author has previewed

Studio rewrites every tag when the preview opens. If the author edited in Studio, never match HTML by
literal text — and do not rebuild over their edits:

```python
import sys; sys.path.insert(0, "scripts")
from edit_helpers import Doc

d = Doc("index.html")
d.replace_el("h-title", '          <div class="pad" id="h-title" style="top:500px;">…</div>')
d.drop_el("e-cursor")
d.retop("e-card", 640)
d.sub(".kc { bottom:196px; }", ".kc { bottom:240px; }")   # CSS / <script> only
d.save()
```

Write the patch as a file with the Write tool — never a heredoc or `python -c` (a `\b` in a regex
became a literal backspace byte twice).
