# Word-level transcription of the voiceover.
#
# This replaces guessing. The heuristic aligner had to infer sentence boundaries from
# pause lengths, and on this recording it kept cutting at 0.09-0.16s gaps while skipping
# 0.50-0.60s gaps a few hundred milliseconds later — boundaries landing early, which is
# exactly the "picture slightly ahead of the voice" the author heard. Raising the seam
# weight to 10x moved nothing, because the rate band was the binding constraint, and
# both candidate assignments were self-consistent. Without hearing the audio there is no
# way to arbitrate between them.
#
# faster-whisper runs on CTranslate2 (no torch), so this is a ~50MB dependency plus the
# model rather than a multi-gigabyte install. Output is words with start/end times,
# which the map can then be built from as measurement instead of inference.
import io
import json
import sys

from faster_whisper import WhisperModel

MODEL = sys.argv[1] if len(sys.argv) > 1 else "small"
AUDIO = sys.argv[2] if len(sys.argv) > 2 else "assets/audio/src/voiceover-master.wav"

print("loading %s ..." % MODEL, flush=True)
model = WhisperModel(MODEL, device="cpu", compute_type="int8")

print("transcribing ...", flush=True)
segments, info = model.transcribe(
    AUDIO,
    language="vi",
    word_timestamps=True,
    vad_filter=False,          # the aligner needs every word, including quiet ones
    beam_size=5,
)

words = []
segs = []
for s in segments:
    segs.append({"start": round(s.start, 3), "end": round(s.end, 3), "text": s.text.strip()})
    for w in (s.words or []):
        words.append({"w": w.word.strip(), "s": round(w.start, 3),
                      "e": round(w.end, 3), "p": round(w.probability, 3)})
    print("  %6.2f-%6.2f  %s" % (s.start, s.end, s.text.strip()[:78]), flush=True)

json.dump({"model": MODEL, "language": info.language,
           "duration": round(info.duration, 3), "segments": segs, "words": words},
          io.open("asr-words.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("\n%d words, %d segments -> asr-words.json" % (len(words), len(segs)))
