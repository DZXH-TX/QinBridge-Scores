import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from build_mainland_mirror import build


def sample(title):
    return json.dumps({"format": "qinbridge.score", "version": 1, "title": title,
                       "sourceUrl": "https://example.com/original", "scoreText": "(AS) D",
                       "settings": {}}, ensure_ascii=False).encode("utf-8")


class MainlandMirrorTests(unittest.TestCase):
    def test_only_chinese_scores_and_generated_catalog_are_published(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "repository"
            chinese = root / "scores" / "zh-CN"
            chinese.mkdir(parents=True)
            raw = sample("中文曲谱")
            (chinese / "中文 #1.qinscore").write_bytes(raw)
            (chinese / "中文 #1.source.json").write_text('{"author":"Source author"}')
            english = root / "scores" / "en-US"
            english.mkdir()
            (english / "English.qinscore").write_bytes(sample("English"))
            (root / "README.md").write_text("Repository source notes")
            (root / "catalog.json").write_text("Stale bilingual catalog must not be copied")
            output = Path(temporary) / "output"
            self.assertEqual(1, build(root, output))
            self.assertEqual({"catalog.json", "scores/zh-CN/中文 #1.qinscore"},
                             {p.relative_to(output).as_posix() for p in output.rglob("*") if p.is_file()})
            self.assertEqual(raw, (output / "scores/zh-CN/中文 #1.qinscore").read_bytes())
            self.assertEqual([{"id": "scores/zh-CN/中文 #1.qinscore", "title": "中文曲谱",
                               "file": "scores/zh-CN/中文 #1.qinscore", "language": "zh-CN"}],
                             json.loads((output / "catalog.json").read_bytes())["scores"])

    def test_invalid_score_leaves_no_uploadable_payload(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            scores = root / "scores" / "zh-CN"
            scores.mkdir(parents=True)
            (scores / "a-valid.qinscore").write_bytes(sample("Valid"))
            (scores / "z-invalid.qinscore").write_text("not a score")
            output = root / "payload"
            with self.assertRaises(ValueError):
                build(root, output)
            self.assertFalse(output.exists())

    def test_removed_scores_disappear_from_the_catalog_and_existing_staging_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            output = root / "payload"
            self.assertEqual(0, build(root, output))
            self.assertEqual([], json.loads((output / "catalog.json").read_bytes())["scores"])
            with self.assertRaisesRegex(ValueError, "must not exist"):
                build(root, output)


if __name__ == "__main__":
    unittest.main()
