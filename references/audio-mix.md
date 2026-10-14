# The mix

## Normalise the voice first

Every video in the series lands at the same loudness only if every voice starts from
the same level. Recordings have arrived at −16.4 (ElevenLabs) and −23.4 LUFS (the
author's own). Bring the voice to **−21.0 LUFS** with a plain gain — no loudnorm, whose
dynamic mode reshapes a TTS delivery:

```bash
ffmpeg -i in.wav -filter:a "volume=+2.4dB" -ar 48000 -ac 1 -c:a pcm_s16le voiceover.wav
# add atempo=1.2 before volume when the author chooses to shorten the read
```

A finished video then measures about −20 LUFS integrated with a true peak under
−1.5 dBTP, matching the channel. The CLI's `hyperframes normalize-audio --reference vo
--target music-bed --write` does the bed-to-voice match by LUFS if you prefer it.

## Compute every gain — this model is validated

```
output dB = file mean dB (over the file's own duration) + 20·log10(gain)
gain      = 10 ^ ((target dB − file mean dB) / 20)
```

Checked against five SFX cues that sat alone in a render: predicted to within
**0.4 dB** every time. Measure each file once, compute, and let the render confirm the
total. Do not tune by differencing renders — a long sound overlapping a short one's
window makes that measurement wrong (see verification.md).

## The house cues — what the author asked for

| cue | file | rule | target | gain |
|---|---|---|---|---|
| thud | `sfx-thud.mp3` (−11.7 dB) | once, t=0 | −22 dB | **0.30** |
| swoosh | `sfx-swoosh.mp3` (−24.9 dB) | every ledger cut | −28 dB | **0.70** |
| pop | `sfx-pop.mp3` (−21.0 dB) | important icons only (house-style §7) | −29 dB | **0.40** |
| pop, in a fast cascade | same | 3+ items < 0.8s apart | −33 dB | **0.26** |
| bed | *Little Things Immaterial* (−16.1 dB) | whole film | −31 dB | **0.18** |

They ship in the skill's `assets/audio/`; `scripts/new-project.py` copies them into the project's
`assets/audio/`. `scripts/add-sfx.py` writes all of them from three lists; the only
per-project edit is those lists.

The cascade rule matters: three pops 0.7s apart at full level read as three
interruptions; 4 dB down they read as one gesture.

## Levels (older recorded-voice projects)

Measure both sides before choosing a gain — never guess from a filename.

```bash
ffmpeg -hide_banner -i voiceover.wav -af ebur128=framelog=quiet -f null - 2>&1 \
  | grep -A1 Integrated | grep 'I:'
```

Typical from this author's recordings: voice **−23 LUFS**, library music **−13 to
−14 LUFS**. To sit the bed ~10 dB under the voice:

```
gain = 10 ^ ((voice_LUFS - 10 - music_LUFS) / 20)
```

−14.2 LUFS music under a −23.1 LUFS voice → **0.12**, landing the bed at −32.6 LUFS.

Then **lift the bed a few dB once the voice stops** so the end card is not silent, and
fade to −60 by the last frame. Use a gain node plus an automation lane rather than a
volume lane: the docs say a GSAP tween on `volume` *replaces* `data-volume` but are
silent on whether a lane replaces or scales it, and a gain stage multiplies correctly
under either reading.

```html
<audio id="music-bed" class="clip" data-start="0" data-duration="106.0"
       src="assets/audio/bed.mp3" data-volume="0.12" data-audio-group="music"
       data-fx-chain='{"version":1,"nodes":[{"type":"gain","id":"bedlevel",
                       "label":"Bed level","params":{"gain":0}}]}'
       data-automation='{"version":1,"lanes":[{"target":"fx.bedlevel.gain","points":[
                        {"t":0,"v":-60},{"t":2.2,"v":0},{"t":98.3,"v":0},
                        {"t":102.0,"v":4},{"t":104.2,"v":4},{"t":106.0,"v":-60}]}]}'></audio>
```

After any preview, confirm `data-fx-chain` and `data-automation` each appear **once** —
Studio drops duplicates and the mix vanishes silently.

## Choosing a bed

Profile the candidates by slicing, not by name or by a single integrated figure:

```bash
for t in 0 10 20 30 40; do
  ffmpeg -hide_banner -ss $t -t 10 -i track.mp3 -af volumedetect -f null - 2>&1 \
    | grep mean_volume
done
```

Pick the passage that matches the narration's emotional register — a dense script
that spends most of its length on doubt wants the softest passage, not the most
driving one. Cutting from a different point in the same track is also how to avoid
three videos in a row sounding identical.

## The sound palette

`scripts/synth-sfx.py` writes eight WAVs as raw samples. It is deliberately **not**
built on ffmpeg `aevalsrc`: those expressions need every comma inside them escaped,
which has silently produced wrong sounds. Plain arithmetic into a `wave` file has no
quoting layer to get wrong and is byte-reproducible.

| sound | length | job |
|---|---|---|
| `bloom` | 1.80s | the opening — a low swell, the only long sound |
| `gen` | 0.75s | a rising "working" tone |
| `done` | 0.55s | two-note confirm |
| `select` | 0.85s | the decision the argument turns on |
| `swipe` | 0.30s | a strike-through |
| `pop` | 0.16s | a card materialising |
| `tick` | 0.10s | a chip or label arriving — plays most often |
| `click` | 0.06s | a cursor |

Any noise must come from a seeded LCG, not `random` — these files are committed and a
re-run must not produce a different swipe.

## Placing them

`scripts/resfx.py` owns every SFX cue: it deletes what it previously wrote and
regenerates, so it is safe to re-run after any retiming. Two rules it encodes:

- **Times are computed with `T()` in Python.** `data-start` is never remapped by the
  runtime, so an authored time written literally drifts by exactly the reader's
  deviation from the estimate.
- **End-card cues are REAL seconds** and must bypass the map — nothing is spoken
  under them, and `T()` past the last anchor extrapolates.

Its cue list mirrors the timeline. **When the timeline is retimed, update it too** — a
cue left behind is a sound with nothing under it.

## Restraint

A video that pings on every element becomes a slot machine. Keep most cues near the
music bed and let only a few be noticed. A healthy hierarchy, measured against a
−23 LUFS voice:

| | relative to voice |
|---|---|
| the one decisive accent | −2 dB |
| opening bloom | −2 dB |
| confirms, strike-throughs | −3 to −5 dB |
| cursor clicks | −7 dB |
| ticks (the most frequent) | −10 dB, about the music bed |
| pops (texture) | −13 dB |

**Nothing should measure louder than the voice.** Two sounds here initially did, both
in the speech band and both over dialogue; they had to come down 6 and 11 dB. Confirm
on the render by differencing — see [verification.md](verification.md).
