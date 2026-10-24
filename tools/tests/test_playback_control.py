import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from validate_scores import resolve_playback_settings, validate_score
import build_catalog
from test_score_security import encode, score
import test_score_security


class PlaybackControlTests(unittest.TestCase):
    def test_shared_client_protocol_cases(self):
        cases = json.loads((Path(__file__).parent / "fixtures/playback-control-cases.json").read_text(encoding="utf-8"))
        for case in cases:
            with self.subTest(name=case["name"]):
                raw = case["json"].encode("utf-8")
                if not case["valid"]:
                    with self.assertRaises((ValueError, UnicodeError)):
                        validate_score(raw)
                    continue
                value = validate_score(raw)
                self.assertEqual(json.loads(case["json"]), value)
                effective, _ = resolve_playback_settings(value["settings"], value.get("playbackControl"))
                self.assertEqual(case["effective"], effective)

    def test_effective_reading_options_are_used(self):
        value = score()
        value.update(version=2, scoreText="BPM:120 4/4\n1/2/3/4/99", playbackControl={"ignoreMeasureNumbers": True})
        value["settings"]["score"]["notation"] = "Numbers"
        self.assertEqual(value, validate_score(encode(value)))
        value["playbackControl"]["ignoreMeasureNumbers"] = False
        with self.assertRaises(ValueError):
            validate_score(encode(value))

    def test_catalog_remains_version_one_for_a_controlled_score(self):
        value = score()
        value.update(version=2, playbackControl={"bpm": 80})
        with tempfile.TemporaryDirectory(prefix="qin-controlled-catalog-") as directory:
            root = Path(directory)
            path = root / "scores/zh-CN/controlled.qinscore"
            path.parent.mkdir(parents=True)
            path.write_bytes(encode(value))
            with patch.object(build_catalog, "ROOT", root):
                build_catalog.main()
            catalog = json.loads((root / "catalog.json").read_text(encoding="utf-8"))
            self.assertEqual(1, catalog["version"])
            self.assertEqual([{"id": "scores/zh-CN/controlled.qinscore", "file": "scores/zh-CN/controlled.qinscore", "title": value["title"], "language": "zh-CN"}], catalog["scores"])

    def test_documented_examples_are_valid(self):
        for path in (Path(__file__).resolve().parents[2] / "examples").glob("*.qinscore"):
            with self.subTest(path=path.name):
                validate_score(path.read_bytes())


class ControlledRepositoryTests(unittest.TestCase):
    setUp = test_score_security.RepositoryTests.setUp
    git = test_score_security.RepositoryTests.git
    commit = test_score_security.RepositoryTests.commit

    def test_controlled_score_can_be_data_only_but_infrastructure_cannot(self):
        value = score()
        value.update(version=2, playbackControl={"bpm": 80, "timing": "SlashBeats"})
        (self.root / self.path).write_bytes(encode(value))
        from validate_scores import validate_repository
        self.assertTrue(validate_repository(self.commit(), self.base, root=self.root, workers=1)["data_only"])
        path = self.root / "tools/validate_scores.py"; path.parent.mkdir(parents=True)
        path.write_text("candidate code must not execute", encoding="utf-8")
        self.assertFalse(validate_repository(self.commit(), self.base, root=self.root, workers=1)["data_only"])
