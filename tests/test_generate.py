import json
import sys
import tempfile
import unittest
from io import StringIO
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from generate import parse, slugify, warn_if_overwriting_different_presentation


class ParseTest(unittest.TestCase):
    def test_leading_heading_starts_a_titled_section(self):
        sections = parse("# Opening\nHello there.\n")
        self.assertEqual(sections, [{"title": "Opening", "chunks": ["Hello there."]}])

    def test_text_before_any_heading_falls_back_to_default_title(self):
        sections = parse("Hello there.\n")
        self.assertEqual(sections, [{"title": "Presentation", "chunks": ["Hello there."]}])

    def test_dashes_split_a_section_into_multiple_chunks(self):
        sections = parse("# Opening\nFirst.\n---\nSecond.\n")
        self.assertEqual(sections, [{"title": "Opening", "chunks": ["First.", "Second."]}])

    def test_multiple_headings_start_new_sections(self):
        sections = parse("# One\nA.\n# Two\nB.\n")
        self.assertEqual(
            sections,
            [{"title": "One", "chunks": ["A."]}, {"title": "Two", "chunks": ["B."]}],
        )

    def test_empty_chunks_are_dropped(self):
        sections = parse("# Opening\n\n---\n\nFirst.\n---\n\n")
        self.assertEqual(sections, [{"title": "Opening", "chunks": ["First."]}])

    def test_trailing_heading_with_no_text_keeps_an_empty_section(self):
        # parse() itself doesn't filter empty sections out; main() does that
        # before writing the manifest, so a chunk-less section is expected here.
        sections = parse("# Opening\nHello.\n# Empty\n")
        self.assertEqual(
            sections,
            [{"title": "Opening", "chunks": ["Hello."]}, {"title": "Empty", "chunks": []}],
        )

    def test_empty_input_yields_no_sections(self):
        self.assertEqual(parse(""), [])


class SlugifyTest(unittest.TestCase):
    def test_lowercases_and_hyphenates_spaces(self):
        self.assertEqual(slugify("My Presentation"), "my-presentation")

    def test_strips_punctuation(self):
        self.assertEqual(slugify("Job, Title (ID: 5)"), "job-title-id-5")

    def test_collapses_repeated_separators(self):
        self.assertEqual(slugify("a---b   c"), "a-b-c")

    def test_falls_back_to_default_when_nothing_alphanumeric_remains(self):
        self.assertEqual(slugify("###"), "presentation")


class WarnIfOverwritingDifferentPresentationTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.out_dir = Path(self.tmp.name) / "some-slug"

    def tearDown(self):
        self.tmp.cleanup()

    def test_no_warning_when_folder_does_not_exist_yet(self):
        with patch("sys.stderr", new=StringIO()) as stderr:
            warn_if_overwriting_different_presentation(self.out_dir, "My Talk")
        self.assertEqual(stderr.getvalue(), "")

    def test_no_warning_when_regenerating_the_same_title(self):
        self.out_dir.mkdir(parents=True)
        (self.out_dir / "manifest.json").write_text(
            json.dumps({"title": "My Talk"}), encoding="utf-8"
        )
        with patch("sys.stderr", new=StringIO()) as stderr:
            warn_if_overwriting_different_presentation(self.out_dir, "My Talk")
        self.assertEqual(stderr.getvalue(), "")

    def test_warns_when_a_different_title_would_be_overwritten(self):
        self.out_dir.mkdir(parents=True)
        (self.out_dir / "manifest.json").write_text(
            json.dumps({"title": "Old Talk"}), encoding="utf-8"
        )
        with patch("sys.stderr", new=StringIO()) as stderr:
            warn_if_overwriting_different_presentation(self.out_dir, "New Talk")
        message = stderr.getvalue()
        self.assertIn("Old Talk", message)
        self.assertIn("New Talk", message)

    def test_no_warning_for_a_malformed_existing_manifest(self):
        self.out_dir.mkdir(parents=True)
        (self.out_dir / "manifest.json").write_text("{not valid json", encoding="utf-8")
        with patch("sys.stderr", new=StringIO()) as stderr:
            warn_if_overwriting_different_presentation(self.out_dir, "New Talk")
        self.assertEqual(stderr.getvalue(), "")


if __name__ == "__main__":
    unittest.main()
