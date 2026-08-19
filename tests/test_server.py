import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from server import list_presentations


def write_manifest(audio_dir, slug, **fields):
    folder = audio_dir / slug
    folder.mkdir(parents=True, exist_ok=True)
    manifest = {
        "title": slug,
        "voice": "am_adam",
        "speed": 0.85,
        "generated_at": None,
        "sections": [],
        **fields,
    }
    (folder / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")


class ListPresentationsTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.audio_dir = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_missing_audio_dir_yields_no_presentations(self):
        missing = self.audio_dir / "does-not-exist"
        self.assertEqual(list_presentations(missing), [])

    def test_folder_without_manifest_is_ignored(self):
        (self.audio_dir / "no-manifest").mkdir()
        self.assertEqual(list_presentations(self.audio_dir), [])

    def test_folder_with_manifest_is_summarized(self):
        write_manifest(
            self.audio_dir,
            "intro",
            title="Intro",
            sections=[{"title": "Opening", "chunks": [{"id": "001"}, {"id": "002"}]}],
        )
        result = list_presentations(self.audio_dir)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["slug"], "intro")
        self.assertEqual(result[0]["title"], "Intro")
        self.assertEqual(result[0]["sections"], 1)
        self.assertEqual(result[0]["chunks"], 2)

    def test_title_falls_back_to_folder_name_when_missing(self):
        folder = self.audio_dir / "untitled"
        folder.mkdir()
        (folder / "manifest.json").write_text(json.dumps({"sections": []}), encoding="utf-8")
        result = list_presentations(self.audio_dir)
        self.assertEqual(result[0]["title"], "untitled")

    def test_most_recently_generated_sorts_first(self):
        write_manifest(self.audio_dir, "older", generated_at="2026-01-01T00:00:00+00:00")
        write_manifest(self.audio_dir, "newer", generated_at="2026-06-01T00:00:00+00:00")
        result = list_presentations(self.audio_dir)
        self.assertEqual([p["slug"] for p in result], ["newer", "older"])

    def test_presentations_without_a_timestamp_sort_last(self):
        write_manifest(self.audio_dir, "timestamped", generated_at="2026-01-01T00:00:00+00:00")
        write_manifest(self.audio_dir, "untimestamped", generated_at=None)
        result = list_presentations(self.audio_dir)
        self.assertEqual([p["slug"] for p in result], ["timestamped", "untimestamped"])

    def test_malformed_manifest_is_skipped_not_raised(self):
        folder = self.audio_dir / "broken"
        folder.mkdir()
        (folder / "manifest.json").write_text("{not valid json", encoding="utf-8")
        write_manifest(self.audio_dir, "fine")
        result = list_presentations(self.audio_dir)
        self.assertEqual([p["slug"] for p in result], ["fine"])


if __name__ == "__main__":
    unittest.main()
