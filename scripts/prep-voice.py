# Level the voiceover to the house loudness (-21.0 LUFS) with a PLAIN GAIN — never loudnorm,
# whose dynamic mode reshapes a delivery — and write the three files the pipeline reads:
#
#   assets/audio/src/voiceover-orig.wav    the recording as received (decoded to WAV)
#   assets/audio/src/voiceover-master.wav  levelled, 48 kHz mono — asr.py, fix-syl.py read this
#   assets/audio/voiceover.mp3             levelled — the film plays this; silences.py reads it
#
# usage (from the project root):
#   python scripts/prep-voice.py "<recording.wav|mp3|m4a>" [--target -21.0] [--tempo 1.0]
# --tempo 1.2 shortens a long read pitch-preserved (atempo, 0.5-2.0) — the author's call, never a default.
import argparse
import os
import re
import shutil
import subprocess

ap = argparse.ArgumentParser()
ap.add_argument("src")
ap.add_argument("--target", type=float, default=-21.0)
ap.add_argument("--tempo", type=float, default=1.0)
a = ap.parse_args()


def lufs(path):
    out = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-af", "ebur128=framelog=quiet",
                          "-f", "null", "-"], capture_output=True, text=True, encoding="utf-8", errors="replace").stderr
    m = re.findall(r"I:\s+(-?[\d.]+) LUFS", out)
    return float(m[-1]) if m else None


def dur(path):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                                capture_output=True, text=True).stdout.strip())


os.makedirs("assets/audio/src", exist_ok=True)
orig = "assets/audio/src/voiceover-orig.wav"
subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", a.src, "-ac", "1", "-ar", "48000",
                "-c:a", "pcm_s16le", orig], check=True)
before = lufs(orig)
assert before is not None, "could not measure the recording"
gain = a.target - before
af = ("atempo=%.4f," % a.tempo if abs(a.tempo - 1.0) > 1e-6 else "") + "volume=%+.2fdB" % gain
master = "assets/audio/src/voiceover-master.wav"
subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", orig, "-af", af, "-ac", "1", "-ar", "48000",
                "-c:a", "pcm_s16le", master], check=True)
subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", master, "-c:a", "libmp3lame", "-q:a", "2",
                "assets/audio/voiceover.mp3"], check=True)
after = lufs("assets/audio/voiceover.mp3")
print("  voice %.1f LUFS -> %+.2f dB -> %.1f LUFS  (target %.1f)" % (before, gain, after, a.target))
print("  duration %.2fs  ->  assets/audio/voiceover.mp3 (+ src/voiceover-orig.wav, src/voiceover-master.wav)"
      % dur("assets/audio/voiceover.mp3"))
if os.path.abspath(a.src) != os.path.abspath(orig) and not os.path.exists("assets/audio/src/" + os.path.basename(a.src)):
    shutil.copy(a.src, "assets/audio/src/" + os.path.basename(a.src))
