#!/usr/bin/env python3
from pathlib import Path
import argparse, json, shutil, subprocess, sys

ROOT = Path(__file__).resolve().parent
AUDIO = ROOT / "audio"
MANIFEST = ROOT / "presentation.json"
MODEL = Path.home() / "kokoro" / "kokoro-v1.0.onnx"
VOICES = Path.home() / "kokoro" / "voices-v1.0.bin"

def parse(text):
    sections, current, pending = [], None, []
    def flush():
        nonlocal pending, current
        chunk = "\n".join(pending).strip()
        pending = []
        if not chunk: return
        if current is None:
            current = {"title": "Presentation", "chunks": []}
            sections.append(current)
        current["chunks"].append(chunk)
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("# "):
            flush()
            current = {"title": s[2:].strip(), "chunks": []}
            sections.append(current)
        elif s == "---":
            flush()
        else:
            pending.append(line)
    flush()
    return sections

p = argparse.ArgumentParser()
p.add_argument("presentation")
p.add_argument("voice", nargs="?", default="am_adam")
p.add_argument("speed", nargs="?", type=float, default=0.85)
a = p.parse_args()

src = Path(a.presentation).expanduser().resolve()
if not src.exists(): sys.exit(f"Presentation not found: {src}")
if not MODEL.exists() or not VOICES.exists(): sys.exit("Kokoro files not found under ~/kokoro")
if shutil.which("kokoro-tts") is None: sys.exit("kokoro-tts is not in PATH")

AUDIO.mkdir(exist_ok=True)
for f in AUDIO.glob("*"):
    if f.is_file(): f.unlink()

manifest = {"voice": a.voice, "speed": a.speed, "sections": []}
n = 0
for section in parse(src.read_text(encoding="utf-8")):
    out = {"title": section["title"], "chunks": []}
    for text in section["chunks"]:
        n += 1
        ident = f"{n:03d}"
        txt, wav = AUDIO/f"{ident}.txt", AUDIO/f"{ident}.wav"
        txt.write_text(text + "\n", encoding="utf-8")
        cmd = ["kokoro-tts", str(txt), str(wav), "--model", str(MODEL),
               "--voices", str(VOICES), "--voice", a.voice, "--speed", str(a.speed)]
        print(f"[{ident}] {section['title']}")
        subprocess.run(cmd, check=True)
        out["chunks"].append({"id": ident, "text": text, "audio": f"audio/{ident}.wav"})
    if out["chunks"]: manifest["sections"].append(out)

MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"Done. Generated {n} chunks.")
