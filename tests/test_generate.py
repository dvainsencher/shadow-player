import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from generate import parse


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


if __name__ == "__main__":
    unittest.main()
