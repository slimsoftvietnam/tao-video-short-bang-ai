---
name: tao-video-short-bang-ai
description: >-
  Build a vertical narrated short (TikTok/Reels/Shorts, 1080x1920) in HyperFrames from a script and
  a voiceover — recorded by the author or a TTS/ElevenLabs read — with picture and voice exactly in
  sync, in the SlimAI house style: a moving paper background, K2D type, violet accents, real logos and
  real footage instead of text, karaoke captions, prompts lit word by word, a comment-box CTA, the house
  sound set (thud, swoosh, pop, laser, shutter, a hand-cut riser, a music bed) and a brand end card.
  Ships a project template, the full pipeline (voice levelling, ASR alignment, syllable times, cut
  points in silence, footage retiming with privacy blur, page captures, captions, SFX premix) and every
  asset it needs. Use this for ANY narrated short: when the user sends a script to make into a video,
  says "làm video", "tạo video tiktok", "đây là file audio nói", "đây là voice", "giọng đọc", "tôi sẽ
  thu âm", sends a .wav/.mp3 of narration, asks to learn the previous video's style ("học phong cách
  video trước"), or says voice and picture do not line up ("chưa khớp", "hình nhanh hơn voice", "mất
  voice"). Load it before designing the first frame — most of the author's corrections were knowable
  from the start.
---

# Narrated short pipeline

Two jobs, in this order of importance:

1. **Build what the author actually wants.** Read
   [references/house-style.md](references/house-style.md) before designing anything. Every rule in it
   came back as a correction at least once. It is the most valuable file here.
2. **Put the picture exactly on the voice.** The rest of this file.

Read `/hyperframes` for routing and `/hyperframes-core` for the composition contract, and load
`/motion-doctrine` for the seams (its `seam-stamp.mjs` and `seam-gate.mjs` run in the pipeline).

## What ships with this skill

| folder | what |
|---|---|
| `template/` | a starter project: `parts/head.part` (the shared component CSS, icon sprite, paper stage), `parts/scenes.part` and `parts/script.js` (example scenes + every timeline helper + the end card at 2x), `package.json` (pinned HyperFrames), `SCRIPT.md` (example) |
| `scripts/` | the pipeline — copied into each project by `new-project.py` ([scripts/README.md](scripts/README.md)) |
| `assets/audio/` | the house sound set: `sfx-thud`, `sfx-swoosh`, `sfx-pop`, `sfx-laser`, `sfx-click` (shutter), `sfx-riser`, `sfx-risercut3` (the riser cut to its climax), `bgm-little-things.mp3` (the bed) |
| `assets/background/` | `paper-bg.mp4` (the moving paper plate, 124 s, 1080×1920) and `paper.webp` (the still plate) |
| `assets/fonts/` | K2D 400–800 as woff2 with its Vietnamese subset (SIL OFL) |
| `assets/logos/` | official marks used by the series (OpenAI, Claude, GitHub, Google G) and `brand-logo.svg`, a placeholder for YOUR end-card logo |

No mascot ships with the skill. Add your own (a transparent `.webm`) if you have one — §Bookends.

**Requirements:** Node 22+, Python 3.10+ (`pip install -r requirements.txt`: faster-whisper, numpy,
Pillow), ffmpeg on PATH, and the HyperFrames skills (`npx --yes hyperframes skills update
motion-doctrine`). HyperFrames itself runs through `npx` at the version pinned in the project's
`package.json`; its first run downloads a headless Chrome, `asr.py`'s first run the Whisper model.

## The order of work

1. **Read house-style.md**, then open the most recent project if there is one and reuse what it
   learned. The channel is a series.
2. **Start the project** (voice first — the common case):
   ```bash
   python "<skill>/scripts/new-project.py" "<folder>" --name "Tên video" --voice "<recording>"
   ```
   It copies the template, the scripts and the assets, and levels the voice to **−21.0 LUFS**
   (`prep-voice.py`, a plain gain).
3. **The script** goes in `SCRIPT.md`, one sentence per plain line, exactly as spoken. Group the
   sentences into scenes in `scripts/plan-beats.py` (`SCENES`).
4. **Align** — every cue is written in recorded seconds:
   ```bash
   python scripts/asr.py small          # -> asr-words.json   (larger model if the match rate < 90%)
   python scripts/plan-beats.py         # -> beats.json       (only a scaffold for the aligner)
   python scripts/align-asr.py          # -> vo-alignment.json (each sentence's real window)
   python scripts/syl-times.py          # -> syl-times.json   (every syllable's time)
   python scripts/fix-syl.py            # starts stamped inside a pause move to the voice
   python scripts/silences.py           # the silent span of every sentence gap: cut there
   ```
5. **Media.** The author's recordings: `scripts/make-media.py` retimes them onto the voice in segments,
   bakes privacy blurs in and cuts what must not be seen. Public pages: `node scripts/cdp.mjs shot
   <url> research/shots/x.png --w 1280 --dpr 2` (own capture, nothing bypassed). Logos: official files
   only — never generated, never traced.
6. **Author the film** in `parts/` (the example scenes show every house pattern) at the times in
   `syl-times.json`; set the cuts in `scripts/build.py` (`SC`) and its other per-project lines
   (`PROMPTS`, `CTA_WORD`, `STEPS`, `BRAND_LOGO`, `SLOGAN`), captions in `scripts/karaoke.py`
   (`SIDES`, `DARK`, `SKIP`), sound in `scripts/add-sfx.py` (`RISER`, `LASER`, `CLICK`, `POP`).
7. **Build and verify** — with snapshots, not renders (below):
   ```bash
   bash scripts/make.sh                 # build.py -> karaoke.py -> seam-stamp -> add-sfx.py
   npm run check
   npx hyperframes snapshot --at 0.6,4.5,9.9,... --no-end -o snapshots/v1
   ```
8. **Open the preview and hand over the link.** `npx hyperframes preview --background`. Never render
   straight after a change — the author has said so twice. **Render only when asked.**

## Two modes

### Voice first — the common case

The author sends the script *and* the recording together. **Author the composition directly in
recorded seconds.** There is no estimate, so there is nothing to remap. Captions come from
`scripts/karaoke.py`; sound from `scripts/add-sfx.py`. Both write plain real seconds.

Dropping the `OLD/NEW → T()` layer removes the single largest source of sync bugs in the earlier
pipeline: `data-start` on `<audio>` was the one attribute `T()` never touched, and every SFX drifted
by the reader's deviation. With no map, what you write is what plays.

### Voice last — the author records after seeing the picture

1. Build against an estimate; `plan-beats.py` writes it as `beats.json`.
2. Hand off the script as text. Wait for the recording.
3. Align, install the map, regenerate captions and SFX (`install-map.py`, `recaption.py`, `resfx.py`).

Every narration-bound cue goes through `T()`, a piecewise-linear map from estimate to recorded time.
**Positions move; durations do not** — where the reader sped up, fixed-length animations can collide.

```js
var OLD = [], NEW = [];      // filled by scripts/install-map.py, which reads it back
var TL = { to: (a,b,t) => tl.to(a,b,T(t)), fromTo: (a,b,c,t) => tl.fromTo(a,b,c,T(t)),
           set: (a,b,t) => tl.set(a,b,T(t)) };
```

Route narration-bound cues through `TL` and **nothing else** — bookends and end cards are raw `tl` in
real seconds; `T()` past the last anchor extrapolates. SFX times must be mapped in Python
(`scripts/resfx.py`) because the runtime never remaps `data-start`.

## Alignment: ASR, never pause heuristics

A pause-length heuristic cut sentences at 0.09s gaps while skipping 0.5s ones and drifted **3.4
seconds** by sentence 18. `align-asr.py` matches script syllables to recognised words by edit
distance, folding diacritics. It prints a match rate — below ~90%, try a larger model.

Two checks before trusting the map:

- **Sentence-rate spread.** Short dramatic lines ("Đừng dừng.") legitimately stretch; a *run* of
  adjacent slow sentences is a misalignment.
- **Rare-word cross-check.** Search `asr-words.json` directly for brand names and numbers, and confirm
  each lands inside the window the map gives its sentence. That is a different code path from the
  matcher, so it catches matcher errors.

`SCRIPT.md` must hold **one sentence per plain line** — `plan-beats.py` skips every line starting with
`#`, `-`, `>` or `|`, so a script written as a markdown table yields zero sentences. Details in
[references/alignment.md](references/alignment.md).

## Verify with frames, not renders

A full render is ~4 minutes. `npx hyperframes snapshot --at t1,t2,… --no-end` is ~23 seconds for a
dozen frames plus a contact sheet. Use snapshots for every picture question and render once, to
deliver.

```bash
npx hyperframes snapshot --at 4,12.5,22,39 --no-end -o snapshots/v1
npx hyperframes snapshot --at 45.5 --no-end --zoom "#b-glyph" -o snapshots/zoom
```

`--zoom` on every icon: it caught a shovel that read as a pen and a coin stack that read as a
database. Snapshot 0.2–0.4 s after every cut: a cut must land on something.

**`check` passing is not evidence.** It stayed green over: an entire film rendering as background plus
captions, a fan diagram rendering as one dot, nine stacked scenes, duplicated caption divs, and every
sync error. It checks structure. Only a frame shows whether the video is right.

**The seams:** `node "<motion-doctrine>/scripts/seam-gate.mjs" verify --ledger ledger.json --url
http://127.0.0.1:3002` against a running preview (set `CHROME_PATH` to HyperFrames' headless Chrome).
Some preview runtimes defer big seeks and report false FAILs — see traps.md.

**Never verify sync against the captions** — they come from the same map. Compare against the
recording: `scripts/audit-sync.py`, the rare-word check, or the author's ears. More in
[references/verification.md](references/verification.md).

## Editing a project the author has previewed

**Studio rewrites `index.html` every time the preview opens** — it injected 507 `data-hf-id`
attributes in one pass and turned `<br />` into `<br>`. Every literal HTML match in a patch script
dies. If the author edited in Studio, patch with `scripts/edit_helpers.py`:

- `replace_el(id, html)` — replace a whole element by id, walking tag depth
- `retop(id, px)` — change one element's `top:` in place
- `sub(old, new)` — literal replace, **only for CSS and `<script>`**, which Studio leaves alone

A file that differs from a fresh build only in serialisation (`data-hf-id`, `&#160;`) holds no author
edits — then edit `parts/` and rebuild with `make.sh`. A Studio tab that says "the preview did not
reload (it took too long)" still shows the old film: reload the page and wait ~20 s.

Write patch scripts with the **Write tool**, never a heredoc or `python -c`: a `\b` in a regex turned
into a literal backspace byte twice in one session.

## Sound

The voice sits at **−21.0 LUFS** (`prep-voice.py`). Every other level is computed, not tuned by ear:

```
output dB = file mean dB + 20·log10(gain)
```

Validated against five isolated cues to ±0.4 dB. The house cues — thud once at 0, swoosh on every
ledger cut, pop only when an important icon appears, laser on a click, shutter on an important number,
the riser cut by hand into the hook, the bed ~12 dB under the voice — are in
[house-style.md §7](references/house-style.md), ship in `assets/audio/` and are placed by
`scripts/add-sfx.py`, which premixes them into one track. Mixing detail and the measurement traps in
[references/audio-mix.md](references/audio-mix.md).

## Bookends

- **Opening mascot** (optional — none ships): your own transparent `.webm`, BIG in the lower-left
  corner with its feet off the frame, 0.25 s to the hook's dead stop; it leaves under the flash so
  nothing sits on a full-screen clip that follows. The slot is commented in `template/parts/scenes.part`.
- **End card**: your logo (`build.py BRAND_LOGO`), an oversized cursor clicks it, the slogan
  (`SLOGAN`) — the house card at 2x, 2.75 s. It is in `template/parts/script.js`.

## Before you touch the file

Read [references/traps.md](references/traps.md). Each entry cost real time. The worst:

- **`.scene { opacity:0 }` makes the whole film invisible.** The framework gates clips by
  `data-start` and never touches opacity. Park the *wrapper* at `autoAlpha:0`.
- **`autoAlpha` only in a `fromTo`'s from-vars is lost once the tween completes.** Put it in the
  to-vars too, or a `tl.set(…autoAlpha:0, 0)` wins on every seek.
- **A timed `<video>` inside a timed scene is a lint error** — a scene that holds a clip is an untimed
  `class="scene"`; the seam-stamped wrapper gates it.
- **DOM order is z-order** — a drawn object added later covers what flies into it.

## When the author says it is still wrong

Take it literally and find which it is — the fixes are opposite:

| They say | Means | Fix |
|---|---|---|
| "hình nhanh hơn voice" | cues fire before their words | the map, or the cue's position |
| "lướt qua nhanh quá" | too little screen time | the duration, or cut something |
| "chưa đẹp", "nhỏ quá" | a house-style miss | re-read house-style.md §3–4 |
| "chưa thể hiện được nội dung" | skeleton where substance was needed | real phrases, §4 |

Answering the wrong one and reporting it fixed is worse than not fixing it. After two attempts that do
not land, stop patching and question the approach.
