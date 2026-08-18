# Shadow Player

Local-only presentation shadowing with Kokoro.

## Format
In `presentation.txt`:
- `# Section title` starts a section.
- `---` starts a new shadowing chunk.
Chunks may be any length.

## Run
```bash
./generate.sh presentation.txt
./start.sh
```
Then open http://127.0.0.1:8000

Default voice: `am_adam`; default generation speed: `0.85`.

Playback speeds: 0.7×, 0.85×, 1.0×, 1.15×, 1.3×, 1.5× (edit the `SPEEDS` array in
`app.js` to change these).

Keyboard: Space play/pause, R repeat, Left/Right navigate, H hide/show text,
number keys select a speed by its position in the list (1 = 0.7×, 2 = 0.85×, …).

Everything stays on the local machine. The server binds only to 127.0.0.1.

## Audio

`audio/` is produced by `./generate.sh` (one `.wav` + `.txt` pair per chunk) and is
gitignored — it's regenerated locally, not committed. `presentation.json` and
`presentation.txt` in this repo are a small sample; running `./generate.sh` on your
own `presentation.txt` overwrites `presentation.json` and regenerates `audio/` to
match.

## Tests

```bash
python3 -m unittest discover -s tests -v
```
Runs on every push/PR via GitHub Actions (`.github/workflows/tests.yml`).
