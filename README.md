# Shadow Player

Local-only presentation shadowing with Kokoro.

## Format
In a presentation `.txt` file (see `presentation.txt` for a sample):
- `# Section title` starts a section.
- `---` starts a new shadowing chunk.
Chunks may be any length.

## Generating a presentation
```bash
./generate.sh presentation.txt
```
This synthesizes one `.wav` per chunk with Kokoro and writes them, alongside a
`manifest.json` and a copy of your input file (`source.txt`), into
`audio/<slug>/` — the slug is derived from the filename (`presentation.txt` →
`audio/presentation/`). Run it again on a different file and it creates a
separate folder, so multiple presentations coexist. Keeping a copy of the
source alongside the audio means each presentation folder is self-contained —
you can find and re-read (or re-generate from) the original text later even if
the file you first pointed `generate.sh` at has since moved or changed.

Give a presentation its own title/folder name instead of deriving one from the
filename:
```bash
./generate.sh cv.txt am_adam 0.85 --name "Acme Corp — Backend Role"
```

## Running the app
```bash
./start.sh
```
Then open http://127.0.0.1:8000. The header has a dropdown to switch between
every presentation you've generated (most recently generated first) — your
choice is remembered across reloads.

Default voice: `am_adam`; default generation speed: `0.85`.

Playback speeds: 0.7×, 0.85×, 1.0×, 1.15×, 1.3×, 1.5× (edit the `SPEEDS` array in
`app.js` to change these).

Keyboard: Space play/pause, R repeat, Left/Right navigate, H hide/show text,
number keys select a speed by its position in the list (1 = 0.7×, 2 = 0.85×, …).

Everything stays on the local machine. The server binds only to 127.0.0.1.

## Audio

`audio/` is entirely gitignored — every presentation's `manifest.json`, `.wav`,
and `.txt` files are generated locally by `./generate.sh`, never committed.
`presentation.txt` in this repo is just a sample input.

## Tests

```bash
python3 -m unittest discover -s tests -p "test_*.py" -v   # generate.py, server.py
node --test                                                 # frontend helpers
```
Both run on every push/PR via GitHub Actions (`.github/workflows/tests.yml`).
