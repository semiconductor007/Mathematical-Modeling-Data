from __future__ import annotations

import unittest

from scripts.validate_modeling import validate


class ModelingValidationTests(unittest.TestCase):
    def test_committed_outputs_are_consistent(self) -> None:
        self.assertEqual(validate(), [])


if __name__ == "__main__":
    unittest.main()
