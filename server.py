#!/usr/bin/env python3
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import json, os

ROOT = Path(__file__).resolve().parent
AUDIO_DIR = ROOT / "audio"


def list_presentations(audio_dir):
    """Scan audio_dir for subfolders holding a manifest.json (i.e. a
    generate.py output) and summarize each one for the picker UI.
    Most recently generated first; folders without a manifest are ignored.
    """
    presentations = []
    if not audio_dir.is_dir():
        return presentations

    for entry in sorted(audio_dir.iterdir()):
        if not entry.is_dir():
            continue
        manifest_path = entry / "manifest.json"
        if not manifest_path.is_file():
            continue
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue

        sections = manifest.get("sections", [])
        chunk_count = sum(len(s.get("chunks", [])) for s in sections)
        presentations.append({
            "slug": entry.name,
            "title": manifest.get("title") or entry.name,
            "voice": manifest.get("voice"),
            "speed": manifest.get("speed"),
            "sections": len(sections),
            "chunks": chunk_count,
            "generatedAt": manifest.get("generated_at"),
        })

    # Missing timestamps sort as "" (the smallest string), so reverse=True
    # naturally puts them last instead of first.
    presentations.sort(key=lambda p: p["generatedAt"] or "", reverse=True)
    return presentations


class Handler(SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def do_GET(self):
        if self.path == "/api/presentations":
            self._send_json(list_presentations(AUDIO_DIR))
            return
        super().do_GET()

    def _send_json(self, data):
        body = json.dumps(data).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main():
    os.chdir(ROOT)
    server = ThreadingHTTPServer(("127.0.0.1", 8000), Handler)
    print("Open http://127.0.0.1:8000")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
