from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.generate_figures import generate


class FigureGenerationTests(unittest.TestCase):
    def test_generates_valid_svg_files(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            paths = generate(Path(folder))
            self.assertEqual(len(paths), 4)
            for path in paths:
                content = path.read_text(encoding="utf-8")
                self.assertTrue(content.startswith("<svg"))
                self.assertIn("</svg>", content)


if __name__ == "__main__":
    unittest.main()
