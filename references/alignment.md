# Aligning the picture to a recorded voice

## Why the obvious approach fails

The tempting method is: detect silences, assume the long ones are sentence ends,
distribute sentences across the speech segments so everyone's reading rate comes out
similar. It produces a plausible-looking table and it is wrong in a way that survives
every automated check.

On the take this skill came from, that solver placed sentence boundaries at gaps of
**0.09s, 0.16s and 0.14s** while ignoring gaps of **0.60s, 0.56s and 0.50s** a few
hundred milliseconds later. Readers pause longest at full stops, so the boundaries
were early — and because each error pushed the next, the drift accumulated:

| sentence | heuristic | true (ASR) | error |
|---|---|---|---|
| 1–14 | — | — | under 0.6s |
| 16 | 61.76 | 63.27 | **1.5s early** |
| 17 | 66.32 | 68.00 | **1.7s early** |
| 18 | 72.36 | 75.60 | **3.2s early** |
| 19 | 76.18 | 79.57 | **3.4s early** |

The first half looked fine, which is exactly why it was reported as fixed twice.

### Things that did not help

- **Raising the seam weight.** From 1.1 to 10 the boundaries did not move by a single
  segment. The rate band, not the seam term, was the binding constraint.
- **Tightening the rate band.** The correct assignment pushed one sentence to 6.58
  syl/s, outside the band, so tightening actively excluded the right answer.
- **Loosening silence detection.** Going from `-34dB:d=0.16` (50 segments) to
  `-28dB:d=0.08` (73 segments) genuinely improved the rate spread from 2.44× to 1.42×
  and was a real improvement — but it still could not tell which of two
  self-consistent assignments was the true one.

Two candidate maps can both be arithmetically consistent. Without hearing the audio
there is nothing left to arbitrate with. That is the moment to stop tuning.

## Use ASR

```bash
python -m pip install faster-whisper
```

CTranslate2-backed, so roughly 50 MB plus the model rather than the multi-gigabyte
torch install. `hyperframes transcribe` exists but needs whisper.cpp built locally,
which may not be present.

```bash
python scripts/asr.py small     # or medium/large-v3 if the match rate is poor
```

Writes `asr-words.json`: every word with `s`/`e` times and a confidence. Set the
language explicitly (`language="vi"`) — auto-detect on a short clip is unreliable.

## Matching script to transcription

`scripts/align-asr.py` aligns the script's syllable stream to the recognised words by
edit distance. The scoring is what makes it robust to Vietnamese ASR error:

| case | cost |
|---|---|
| exact syllable match | 0.00 |
| matches after folding diacritics | 0.25 |
| different syllable | 1.00 |
| insertion / deletion either side | 0.70 |

Diacritic folding treats `đ` explicitly — it is a distinct letter, not a combining
mark, so NFD decomposition alone will not fold it.

Whisper sometimes emits several syllables in one token; the script splits those and
divides the token's span proportionally, so every syllable carries a time.

A sentence boundary is placed **midway through the silence** between one sentence's
last word and the next sentence's first — so no cue fires while the previous line is
still being spoken, nor after the next has begun.

### Reading the output

```
  script 346 syllables · heard 346 syllables · audio 99.01s
  matched 346/346 syllables (100.0%), 343 exact (99.1%)
```

- **Below ~90% exact** — do not trust the map. Try a larger model first; if it is
  still poor, the recording may not be the script.
- The script prints an **unscripted tail** if the audio runs past the last matched
  word. A real tail means the reader added something and it needs a caption. A tail
  reported by the *heuristic* aligner and not by the ASR one was an artifact of bad
  boundaries — that happened here, a phantom 2.64s that did not exist.

## Sanity checks on any map

- **Per-chapter stretch ratios should cluster near 1.0** if the syllable-rate estimate
  was reasonable. Ratios of 0.69 and 1.23 in the same video were alignment error, not
  the reader speeding up and slowing down. Once corrected, every chapter landed
  between 0.92 and 1.08.
- **Adjacent sentences at wildly different rates is a red flag.** 2.80 vs 7.56 syl/s
  next to each other is not something a human does; it is a boundary in the wrong
  place. Under 1.5× spread across the whole read is healthy.
- **Do not force the first sentence to zero.** A take with 0.5s of room tone at the
  head will fire every opening cue half a second before the first word.

## Placing cues once the map is right

With word-level times available, stop estimating positions inside a sentence.
`scripts/word-times.py` takes a phrase, finds it in the transcription, and inverts the
map to give the **authored** time to write into the timeline:

```
  cum tu                              thuc te   authored
  tao ra poster                         10.46      10.54
  xoa nen                               12.26      12.20
  biet danh gia                         70.06      74.17
```

Place a 0.4–0.5s entrance slightly *before* its phrase so it finishes as the word
lands. A label placed by even division inside a sentence will be a beat out whenever
the phrase is not where a linear model puts it — which is most of the time, because
readers front-load their pauses.

## Reader pace, for the initial estimate

Measured on this author: **3.62 syllables/second wall-clock**, including
inter-sentence pauses. It predicted a 103.7s script that came back at 99.0s — 4.7%
out, and the per-chapter error was under 8% once the alignment was correct. Vietnamese
is monosyllabic in writing, so whitespace tokens count as syllables.

Use ~0.35s between sentences and ~0.55s after a question when building the estimate.
