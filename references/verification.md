# Verifying, without fooling yourself

## The circular check

**Captions are generated from the timing map.** Checking the picture against the
captions therefore cannot detect a shifted map — the picture and the captions shift
together and agree perfectly. In the session this skill came from, that check was run
twice, reported as passing twice, and was worthless both times. The author found the
error by listening.

Any verification of sync has to compare against something the map did not produce:

1. **`scripts/audit-sync.py <from> <to>`** — maps every cue's authored time forward
   and reports which *recorded* sentence is playing then, and how far into it. It
   filters out caption cues on purpose. A cue firing in the sentence before the one it
   illustrates is the picture running ahead of the voice.
2. **`scripts/word-times.py`** — the measured time of a phrase. If a label is supposed
   to land on "xóa nền", this says exactly when "xóa nền" is said.
3. **The rendered MP4.** Measure it. See below.
4. **The author's ears.** When they say it is still wrong after two attempts, they are
   right and the model is wrong.

## `check` is not evidence

`npm run check` passed over every one of these:

- **an entire film rendering as background plus captions** — `.scene { opacity:0 }`
- **a five-path diagram rendering as a single dot** — `autoAlpha` in from-vars only
- **105 caption divs duplicated outside their container**
- nine scenes stacked on top of each other, because `style="top:1920"` has no unit
- a background video completely hidden behind an opaque `#bg`
- a headline visible for 0.47 seconds
- every sync error described in [alignment.md](alignment.md)
- panels at 4.5% opacity that measured 16:1 contrast and still could not be read

It catches structural mistakes. It cannot see whether the video is any good, or
whether anything lines up. Its own warnings can also be architecture false positives
(`#camera` overflow on a camera-over-workspace build) — so neither its green nor its
yellow is a verdict.

## Snapshot first — render last

A render is ~4 minutes; a dozen snapshots plus a contact sheet is ~23 seconds. Every
picture question goes to snapshots. Across two projects, eleven full renders were run
and only one was a delivery — the rest were being used as a measuring instrument.

```bash
# one frame at the middle of every scene, after every structural change
npx hyperframes snapshot --at 4,12.5,22,39,52,65 --no-end -o snapshots/v1

# every icon and glyph, at 3x density — the only way a bad glyph gets caught
npx hyperframes snapshot --at 45.5 --no-end --zoom "#b-glyph" -o snapshots/zoom
```

- **Take snapshot times from the recording** (`vo-alignment.json`), not from the
  composition. A frame chosen at "the middle of scene 5 per the timeline" cannot reveal
  a timeline that is wrong.
- **The contact sheet can lie at its edges.** Faint text at the top of a cell was
  bleed from the row below, not a stray caption. Open the full-resolution PNG before
  acting on something seen only in the grid.
- **Snapshot mid-reveal on purpose.** A scene looks empty at a time before its staged
  reveals land; that is a planning signal (is the frame dead for too long?), not
  necessarily a bug.

## Measuring audio without getting a wrong number

Four ways to produce a confident wrong measurement, all of which happened:

**Grepping too loosely.** `volumedetect` prints a histogram after the summary;
`grep -oE '\-?[0-9.]+'` picks up those numbers too. Anchor on the label:

```bash
ffmpeg -hide_banner -ss 20 -t 1 -i in.mp4 -af volumedetect -f null - 2>&1 \
  | grep -E 'mean_volume|max_volume'
```

**Window longer than the sound.** Measuring a 0.06s click over a 0.9s window dilutes
its mean by ~12 dB and makes a perfectly audible sound look absent. This produced a
"KHÔNG NGHE THẤY" verdict on eight sounds that were all fine. **Match the window to
the sound's duration.**

**`astats` with `reset`** returns a *running* average, not per-slice energy — the
curve converges monotonically no matter what the audio does. To profile a track over
time, slice it and measure each slice separately.

**`-v error`** suppresses `volumedetect`'s output entirely — and `psnr`'s, and
`loudnorm`'s. Use `-hide_banner -nostats`.

**A long sound overlapping the window.** A 3.11s thunder covered three short cues at
the head of the video. Their windows measured +7.8 dB over the voice; one was cut from
0.24 to 0.07 gain. Comparing two renders showed the whole 4 dB change tracked the
thunder alone — the short cue had never been loud. Worse, thunder's own "clean" window
sat 2.1s into its decay tail and read 11 dB too quiet. **Before trusting any window,
list every cue whose span overlaps it.**

**The way out: stop measuring the mix and predict it.** Output level is
`file mean dB + 20·log10(gain)`. Measure each SFX file once over its own duration, and
check the model against the few cues that sit alone in the render. It predicted five
of them within 0.4 dB — after which the overlapped cues can be set by calculation and
the render confirms the total. See [audio-mix.md](audio-mix.md).

Also: the `movie=` filter cannot parse a Windows drive-letter colon.

## Proving a sound actually reached the render

Peak level is useless when speech dominates the window. **Difference two renders** —
one before the change, one after. Voice and music are byte-identical, so what remains
is exactly what you added:

```bash
ffmpeg -i new.mp4 -i old.mp4 -filter_complex \
  "[0:a]aformat=sample_fmts=fltp[a];[1:a]aformat=sample_fmts=fltp,volume=-1[b];\
   [a][b]amix=inputs=2:normalize=0[d]" -map "[d]" -c:a pcm_s16le diff.wav
```

Then measure `diff.wav` at each cue's real `data-start`, with a duration-matched
window, and compare against a window where no cue exists — that is the AAC noise
floor (about −50 dB at a 0.10s window). A cue **15 dB or more above the floor** is
present. Read the cue times out of `index.html` rather than recomputing them.

## Verifying the picture

- Snapshot at real times and read the caption in the frame against what the alignment
  says is being spoken then.
- Extract frames from the **render**, not just snapshots, for anything involving
  video backgrounds, blur, or opacity — the render is the artifact.
- For a looping background, judge the seam by comparing loop-point PSNR against
  **consecutive-frame** PSNR. A seam at 30.6 dB against a 41.0 dB baseline is a
  visible jump; after a ping-pong fix, 38.5 dB against the same baseline is not.

## Reporting

State what was measured and what was not. "The render measures clean at both windows;
I could not reproduce the preview behaviour" is a useful report. "Fixed" is not, when
the thing measured was not the thing reported.

If a previous claim turns out to be wrong — a phantom tail, a stretch ratio that was
alignment error, a sound declared inaudible by a bad measurement — correct it plainly
and move on. Those three all happened here.
