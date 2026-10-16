# Free Vietnamese voiceover with Microsoft Edge TTS (the `edge-tts` package — no account, no API key).
#
# Reads SCRIPT.md (one sentence per plain line, the same file the aligner reads), speaks each sentence
# separately, and joins them with a short silence, so every sentence gap is a clean cut point for
# silences.py. Writes assets/audio/src/tts-voice.wav, then levels it with prep-voice.py (-21.0 LUFS)
# unless --no-prep. From there the pipeline is the usual voice-first chain (asr.py, align-asr.py, …).
#
# usage (from the project root):
#   python scripts/tts.py                                  # vi-VN-HoaiMyNeural (female)
#   python scripts/tts.py --voice vi-VN-NamMinhNeural      # male
#   python scripts/tts.py --rate +10% --pitch +0Hz --gap 0.35
#   python scripts/tts.py --list                           # every Vietnamese voice on offer
#
# Needs internet (the voice is synthesised by Microsoft's online service). It is a fallback: a voice the
# author records, or a paid TTS the author already uses (ElevenLabs …), is preferred — ask first.
import argparse
import asyncio
import io
import os
import subprocess
import sys
import tempfile

try:
    import edge_tts
except ImportError:
    sys.exit("edge-tts is missing: python -m pip install --user edge-tts   (or run CAI-DAT.bat again)")

ap = argparse.ArgumentParser()
ap.add_argument("--voice", default="vi-VN-HoaiMyNeural")
ap.add_argument("--rate", default="+0%", help="speed, e.g. +10%% or -5%%")
ap.add_argument("--pitch", default="+0Hz")
ap.add_argument("--gap", type=float, default=0.35, help="silence between sentences (s); 0.55 after a question")
ap.add_argument("--script", default="SCRIPT.md")
ap.add_argument("--no-prep", action="store_true")
ap.add_argument("--list", action="store_true")
a = ap.parse_args()

if a.list:
    voices = asyncio.run(edge_tts.list_voices())
    for v in voices:
        if v["Locale"].startswith("vi-"):
            print("%-24s %s" % (v["ShortName"], v["Gender"]))
    sys.exit(0)

SENT = [s.strip() for s in io.open(a.script, encoding="utf-8").read().split("\n")
        if s.strip() and not s.strip().startswith(("#", "-", ">", "|"))]
if not SENT:
    sys.exit("%s has no sentences — one sentence per plain line" % a.script)

SR = 48000
tmp = tempfile.mkdtemp(prefix="tts-")


async def speak(i, text):
    out = os.path.join(tmp, "s%03d.mp3" % i)
    for attempt in range(3):
        try:
            await edge_tts.Communicate(text, a.voice, rate=a.rate, pitch=a.pitch).save(out)
            return out
        except Exception as e:                     # the service drops a request now and then
            if attempt == 2:
                raise SystemExit("TTS failed on sentence %d (%s): %s" % (i + 1, text[:40], e))
            await asyncio.sleep(2)


async def main():
    return [await speak(i, s) for i, s in enumerate(SENT)]


files = asyncio.run(main())
lst = os.path.join(tmp, "list.txt")
with io.open(lst, "w", encoding="utf-8") as f:
    for i, (p, s) in enumerate(zip(files, SENT)):
        wav = p[:-4] + ".wav"
        # trim the service's own lead/tail silence so the gaps below are exact
        subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", p, "-ac", "1", "-ar", str(SR),
                        "-af", "silenceremove=start_periods=1:start_threshold=-50dB,areverse,"
                               "silenceremove=start_periods=1:start_threshold=-50dB,areverse",
                        wav], check=True)
        f.write("file '%s'\n" % wav.replace("\\", "/"))
        if i + 1 < len(SENT):
            gap = a.gap + (0.2 if s.endswith("?") else 0.0)
            sil = os.path.join(tmp, "g%03d.wav" % i)
            subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "lavfi", "-i",
                            "anullsrc=r=%d:cl=mono" % SR, "-t", "%.3f" % gap, sil], check=True)
            f.write("file '%s'\n" % sil.replace("\\", "/"))

os.makedirs("assets/audio/src", exist_ok=True)
out = "assets/audio/src/tts-voice.wav"
subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst,
                "-af", "apad=pad_dur=0.4", "-c:a", "pcm_s16le", out], check=True)
print("  %d sentences, voice %s (rate %s) -> %s" % (len(SENT), a.voice, a.rate, out))
if not a.no_prep:
    subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "prep-voice.py"), out],
                   check=True)
