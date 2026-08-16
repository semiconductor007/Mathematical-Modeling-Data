from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts import fetch_artificial_analysis_efficiency as collector


class CollectorTests(unittest.TestCase):
    def test_extracts_allow_listed_provider_metrics(self) -> None:
        item = (
            '{"id":"1","slug":"provider_model","host":{"name":"Provider",'
            '"label":"Provider"},"model":{"slug":"model-slug"},'
            '"performance":{"outputSpeed":{"median":12.5},'
            '"timeToFirstToken":{"median":1.25},'
            '"endToEndResponseTime":{"totalTime":41.25}},'
            '"jsonMode":true}'
        )
        page = (
            "Time to First Token Output Speed End-to-End Response Time "
            "Seconds to output 500 tokens " + item
        )
        matches = collector.provider_objects(page, "model-slug")
        self.assertEqual(len(matches), 1)
        self.assertEqual(
            collector.find_metric_values(matches[0]),
            {
                "Time to First Token": "1.25",
                "Output Speed": "12.5",
                "End-to-End Response Time": "41.25",
            },
        )
        self.assertTrue(all(collector.metric_labels(page).values()))

    def test_missing_metric_fails_closed(self) -> None:
        item = {
            "performance": {
                "outputSpeed": {"median": 12.5},
                "timeToFirstToken": {"median": 1.25},
                "endToEndResponseTime": {},
            }
        }
        values = collector.find_metric_values(item)
        self.assertEqual(values["End-to-End Response Time"], collector.MISSING)

    def test_identical_evidence_is_not_appended_twice(self) -> None:
        row = {field: "value" for field in collector.FIELDS}
        row.update(
            {
                "model_id": "model",
                "configuration": "config",
                "provider": "provider",
                "metric": "Output Speed",
                "source_url": "https://artificialanalysis.ai/models/model/providers",
                "retrieval_date": "2026-08-16",
                "content_hash": "hash",
                "raw_display_value": "12.5",
            }
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "staging.csv"
            self.assertEqual(collector.write_rows(path, [], [row]), 1)
            old_rows = collector.existing_rows(path)
            self.assertEqual(collector.write_rows(path, old_rows, [row]), 0)
            self.assertEqual(len(collector.existing_rows(path)), 1)


if __name__ == "__main__":
    unittest.main()
