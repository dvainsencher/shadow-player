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

Keyboard: Space play/pause, R repeat, Left/Right navigate, H hide/show text, 1=0.85x, 2=1.0x, 3=1.15x.

Everything stays on the local machine. The server binds only to 127.0.0.1.
