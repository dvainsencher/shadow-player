#!/usr/bin/env python3
from datetime import datetime, timezone
from pathlib import Path
import argparse, json, re, shutil, subprocess, sys

ROOT = Path(__file__).resolve().parent
AUDIO = ROOT / "audio"
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

def slugify(name):
    """Turn a presentation title into a filesystem- and URL-safe folder name."""
    slug = re.sub(r"[^a-z0-9]+", "-", name.strip().lower()).strip("-")
    return slug or "presentation"

def warn_if_overwriting_different_presentation(out_dir, title):
    """Two different titles can slugify to the same folder (e.g. "Q1 Report" and
    "Q1, Report!" both become audio/q1-report/). Regenerating silently overwrites
    whatever was there, so warn when that's about to replace a different
    presentation rather than just refresh the same one.
    """
    manifest_path = out_dir / "manifest.json"
    if not manifest_path.is_file():
        return
    try:
        existing_title = json.loads(manifest_path.read_text(encoding="utf-8")).get("title")
    except (json.JSONDecodeError, OSError):
        return
    if existing_title and existing_title != title:
        print(
            f"Warning: audio/{out_dir.name}/ already holds \"{existing_title}\" — "
            f"overwriting it with \"{title}\" (both slugify to the same folder name).",
            file=sys.stderr,
        )


def copy_source_into(out_dir, src):
    """Copy the original input file into its presentation folder, so the
    source text travels with the generated audio instead of only existing
    wherever the caller's file happened to live. Returns the copy's filename.
    A no-op if src already *is* that destination (e.g. regenerating from a
    previously-copied source.txt in place).
    """
    dest = out_dir / f"source{src.suffix}"
    if src.resolve() != dest.resolve():
        shutil.copy2(src, dest)
    return dest.name


def main():
    p = argparse.ArgumentParser()
    p.add_argument("presentation")
    p.add_argument("voice", nargs="?", default="am_adam")
    p.add_argument("speed", nargs="?", type=float, default=0.85)
    p.add_argument("--name", help="Presentation title / audio/ subfolder name "
                                  "(default: derived from the input filename)")
    a = p.parse_args()

    src = Path(a.presentation).expanduser().resolve()
    if not src.exists(): sys.exit(f"Presentation not found: {src}")
    if not MODEL.exists() or not VOICES.exists(): sys.exit("Kokoro files not found under ~/kokoro")
    if shutil.which("kokoro-tts") is None: sys.exit("kokoro-tts is not in PATH")

    title = a.name or src.stem
    slug = slugify(title)
    out_dir = AUDIO / slug
    warn_if_overwriting_different_presentation(out_dir, title)
    out_dir.mkdir(parents=True, exist_ok=True)
    for f in out_dir.glob("*"):
        # Don't delete src itself if it's already sitting in out_dir (e.g.
        # regenerating in place from a previously-copied source.txt) — it
        # needs to survive to be read below and re-copied by copy_source_into.
        if f.is_file() and f.resolve() != src.resolve():
            f.unlink()
    source_filename = copy_source_into(out_dir, src)

    manifest = {
        "title": title,
        "voice": a.voice,
        "speed": a.speed,
        "source": source_filename,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "sections": [],
    }
    n = 0
    for section in parse(src.read_text(encoding="utf-8")):
        out = {"title": section["title"], "chunks": []}
        for text in section["chunks"]:
            n += 1
            ident = f"{n:03d}"
            txt, wav = out_dir/f"{ident}.txt", out_dir/f"{ident}.wav"
            txt.write_text(text + "\n", encoding="utf-8")
            cmd = ["kokoro-tts", str(txt), str(wav), "--model", str(MODEL),
                   "--voices", str(VOICES), "--voice", a.voice, "--speed", str(a.speed)]
            print(f"[{ident}] {section['title']}")
            subprocess.run(cmd, check=True)
            # Audio path is relative to this presentation's own folder, not the
            # repo root — the frontend resolves it against audio/<slug>/.
            out["chunks"].append({"id": ident, "text": text, "audio": f"{ident}.wav"})
        if out["chunks"]: manifest["sections"].append(out)

    manifest_path = out_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Done. Generated {n} chunks into audio/{slug}/")


if __name__ == "__main__":
    main()
