import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from validate_scores import SCORE_BYTES, SOURCE_BYTES, strict_json, validate_repository, validate_score, validate_source_note
import score_automation


def score():
    return {"format": "qinbridge.score", "version": 1, "title": "测试 · Song", "sourceUrl": "",
            "scoreText": "[(AS)(DQ)] / (A[SD]) /", "settings": {"score": {"notation": "Keyboard", "timing": "SlashBeats"}}}


def encode(value):
    return json.dumps(value, ensure_ascii=False).encode("utf-8")


class JsonAndScoreTests(unittest.TestCase):
    def test_existing_format_and_parallel_note_groups(self):
        sample = score()
        self.assertEqual(sample, validate_score(encode(sample)))
        sample["scoreText"] = "［（1+1）（2+2）］ /0 /"
        sample["settings"]["score"]["notation"] = "Numbers"
        self.assertEqual(sample, validate_score(encode(sample)))

    def test_unknown_executable_fields_are_rejected_at_every_level(self):
        for location in ((), ("settings",), ("settings", "score")):
            with self.subTest(location=location):
                sample = score()
                target = sample
                for key in location:
                    target = target[key]
                target["onLoad"] = "powershell malicious.ps1"
                with self.assertRaises(ValueError):
                    validate_score(encode(sample))

    def test_duplicate_keys_and_nonstandard_json_are_rejected(self):
        for raw in (b'{"a":1,"a":2}', b'{"a":1,"\\u0061":2}', b'{"a":NaN}', b'{"a":Infinity}',
                    b'{"a":1e999}', b'{"a":123456789012345678901234567890123456789}', b'{"a":1,}',
                    b'{}; exec("payload")', b'{"a":"\xff"}', b'{/*comment*/"a":1}', b'[' * 13 + b'0' + b']' * 13):
            with self.subTest(raw=raw):
                with self.assertRaises((ValueError, UnicodeError)):
                    strict_json(raw, SCORE_BYTES)

    def test_size_limit_is_checked_before_parsing(self):
        with self.assertRaisesRegex(ValueError, "byte limit"):
            validate_score(b" " * (SCORE_BYTES + 1))

    def test_script_text_is_not_a_score_and_metadata_stays_inert(self):
        sample = score()
        sample["title"] = "$(touch attack) <script>text</script>"
        self.assertEqual(sample["title"], validate_score(encode(sample))["title"])
        for text in ("__import__('os').system('attack')", "<script>alert(1)</script>", "A; whoami", "(AA)", "[(AS]DQ)", "0 /", "(" * 33 + "A" + ")" * 33):
            sample["scoreText"] = text
            with self.subTest(text=text), self.assertRaises(ValueError):
                validate_score(encode(sample))

    def test_settings_require_finite_typed_numbers(self):
        for key, value in (("gate", True), ("gate", "0.7"), ("slotMilliseconds", -1),
                           ("minimumTriggerIntervalMilliseconds", 0), ("arpeggioMilliseconds", 101),
                           ("rhythm", {"bpm": 0}), ("rhythm", {"unitsPerBeat": True}),
                           ("score", {"notation": 1}), ("score", {"ignoreMeasureNumbers": "false"})):
            sample = score()
            sample["settings"][key] = value
            with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                validate_score(encode(sample))
        sample = score()
        sample["version"] = True
        with self.assertRaises(ValueError):
            validate_score(encode(sample))

    def test_active_source_schemes_and_metadata_controls_are_rejected(self):
        for source in ("javascript:alert(1)", "file:///C:/evil.ps1", "https://user:password@example.com", "https://example.com\n::warning::payload"):
            sample = score()
            sample["sourceUrl"] = source
            with self.subTest(source=source), self.assertRaises(ValueError):
                validate_score(encode(sample))


class RepositoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="qin-score-tests-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.git("init", "-q")
        self.git("config", "user.name", "Score tests")
        self.git("config", "user.email", "score-tests@example.invalid")
        self.path = "scores/zh-CN/song.qinscore"
        file = self.root / self.path
        file.parent.mkdir(parents=True)
        file.write_bytes(encode(score()))
        self.catalog = {"format": "qinbridge.catalog", "version": 1, "scores": [
            {"id": self.path, "title": score()["title"], "file": self.path, "language": "zh-CN"}]}
        (self.root / "catalog.json").write_bytes(encode(self.catalog))
        self.base = self.commit()

    def git(self, *args, data=None):
        return subprocess.run(["git", "-C", str(self.root), *args], input=data, capture_output=True, check=True).stdout.decode().strip()

    def commit(self):
        self.git("add", ".")
        self.git("commit", "-qm", "fixture")
        return self.git("rev-parse", "HEAD")

    def test_data_only_candidate_is_validated_without_checkout(self):
        (self.root / "catalog.json").write_bytes(encode(self.catalog) + b"\n")
        head = self.commit()
        # Corrupting a working file must not change immutable-commit validation.
        (self.root / self.path).write_text("not JSON", encoding="utf-8")
        result = validate_repository(head, self.base, root=self.root, workers=2)
        self.assertTrue(result["data_only"])
        self.assertEqual(1, result["scores"])

    def test_workflow_or_script_change_cannot_receive_automatic_approval(self):
        for path in (".github/workflows/evil.yml", "tools/evil.py", "payload.ps1"):
            file = self.root / path
            file.parent.mkdir(parents=True, exist_ok=True)
            file.write_text("untrusted code", encoding="utf-8")
        result = validate_repository(self.commit(), self.base, root=self.root, workers=1)
        self.assertFalse(result["data_only"])

    def test_catalog_cannot_disguise_missing_duplicate_or_external_files(self):
        for entries in ([], self.catalog["scores"] * 2,
                        [{**self.catalog["scores"][0], "file": "https://example.com/evil.json"}],
                        [{**self.catalog["scores"][0], "title": "different"}]):
            (self.root / "catalog.json").write_bytes(encode({**self.catalog, "scores": entries}))
            with self.subTest(entries=entries), self.assertRaises(ValueError):
                validate_repository(self.commit(), self.base, root=self.root, workers=1)

    def test_git_symlink_and_executable_modes_are_rejected(self):
        oid = self.git("rev-parse", f"{self.base}:{self.path}")
        for mode in ("120000", "100755"):
            self.git("update-index", "--cacheinfo", mode, oid, self.path)
            tree = self.git("write-tree")
            head = self.git("commit-tree", tree, "-p", self.base, "-m", "untrusted mode")
            with self.subTest(mode=mode), self.assertRaisesRegex(ValueError, "non-executable"):
                validate_repository(head, self.base, root=self.root, workers=1)

    def test_non_score_file_in_score_directory_is_rejected(self):
        (self.root / "scores/zh-CN/evil.py").write_text("payload", encoding="utf-8")
        with self.assertRaises(ValueError):
            validate_repository(self.commit(), self.base, root=self.root, workers=1)

    def test_optional_source_note_is_auto_eligible_without_any_cc_license(self):
        note = self.root / (self.path + ".source.json")
        note.write_bytes(encode({"sourceUrl": "https://example.com/original", "author": "谱面作者"}))
        result = validate_repository(self.commit(), self.base, root=self.root, workers=2)
        self.assertTrue(result["data_only"])
        self.assertEqual(1, result["source_notes"])
        self.assertEqual(1, result["scores"])

    def test_source_note_accepts_other_license_text_without_verifying_permission(self):
        note = self.root / (self.path + ".source.json")
        note.write_bytes(encode({"author": "谱面作者", "license": "未经作者许可不得转载", "notes": "授权情况另行确认"}))
        self.assertTrue(validate_repository(self.commit(), self.base, root=self.root, workers=1)["data_only"])

    def test_orphan_source_note_is_rejected(self):
        (self.root / "scores/zh-CN/missing.qinscore.source.json").write_bytes(b'{}')
        with self.assertRaisesRegex(ValueError, "accompany"):
            validate_repository(self.commit(), self.base, root=self.root, workers=1)

    def test_source_notes_cannot_hide_executable_fields_or_oversized_blobs(self):
        note = self.root / (self.path + ".source.json")
        for raw in (b'{"onLoad":"payload"}', b'{"author":"a","author":"b"}',
                    b'{"sourceUrl":"javascript:payload"}', b' ' * (SOURCE_BYTES + 1)):
            note.write_bytes(raw)
            with self.subTest(raw=raw[:70]), self.assertRaises(ValueError):
                validate_repository(self.commit(), self.base, root=self.root, workers=1)

    def test_source_note_symlink_and_executable_modes_are_rejected(self):
        path = self.path + ".source.json"
        (self.root / path).write_bytes(b'{"author":"A"}')
        commit = self.commit()
        oid = self.git("rev-parse", f"{commit}:{path}")
        for mode in ("120000", "100755"):
            self.git("update-index", "--cacheinfo", mode, oid, path)
            tree = self.git("write-tree")
            head = self.git("commit-tree", tree, "-p", commit, "-m", "untrusted source mode")
            with self.subTest(mode=mode), self.assertRaisesRegex(ValueError, "non-executable"):
                validate_repository(head, self.base, root=self.root, workers=1)

    def test_deleting_optional_source_note_remains_auto_eligible(self):
        note = self.root / (self.path + ".source.json")
        note.write_bytes(b'{"author":"A"}')
        with_note = self.commit()
        note.unlink()
        result = validate_repository(self.commit(), with_note, root=self.root, workers=1)
        self.assertTrue(result["data_only"])
        self.assertEqual(0, result["source_notes"])

    def test_sidecar_does_not_make_an_infrastructure_change_auto_eligible(self):
        (self.root / (self.path + ".source.json")).write_bytes(b'{"author":"A"}')
        (self.root / "README.md").write_text("Changed policy", encoding="utf-8")
        result = validate_repository(self.commit(), self.base, root=self.root, workers=1)
        self.assertFalse(result["data_only"])


class SourceNoteTests(unittest.TestCase):
    def test_license_can_be_omitted_empty_or_any_plain_text(self):
        for note in ({}, {"author": "作者"}, {"license": ""}, {"license": "CC BY-SA 4.0"}, {"license": "All rights reserved"}):
            with self.subTest(note=note):
                self.assertEqual(note, validate_source_note(encode(note)))

    def test_fields_are_text_not_executable_objects(self):
        for note in ({"author": {"$type": "Process"}}, {"license": ["CC BY-SA 4.0"]}, {"notes": "\n::warning::payload"}):
            with self.subTest(note=note), self.assertRaises(ValueError):
                validate_source_note(encode(note))


class ApprovalTests(unittest.TestCase):
    def setUp(self):
        self.head, self.base = "a" * 40, "b" * 40
        self.pr = {"state": "open", "draft": False, "head": {"sha": self.head}, "base": {"sha": self.base, "ref": "main"}}
        self.calls = []
        self.environment = patch.dict(os.environ, {"PR_NUMBER": "7", "HEAD_SHA": self.head, "BASE_SHA": self.base,
            "VALIDATION_RESULT": "success", "AUTO_ELIGIBLE": "true", "GITHUB_RUN_ID": "123"})
        self.environment.start()
        self.addCleanup(self.environment.stop)

    def api(self, path, method="GET", data=None):
        self.calls.append((path, method, data))
        if method == "GET":
            return [] if "/reviews?" in path else copy.deepcopy(self.pr)
        return {"merged": True}

    def test_approval_and_merge_are_bound_to_the_validated_commit(self):
        with patch.object(score_automation, "api", self.api):
            score_automation.publish()
        self.assertEqual(self.head, next(data["commit_id"] for path, method, data in self.calls if path.endswith("/reviews")))
        self.assertEqual({"sha": self.head, "merge_method": "squash"}, self.calls[-1][2])

    def test_new_head_or_base_never_gets_approved_using_old_results(self):
        for field in ("head", "base"):
            original = self.pr[field]["sha"]
            self.pr[field]["sha"] = "c" * 40
            self.calls.clear()
            with patch.object(score_automation, "api", self.api), self.assertRaises(ValueError):
                score_automation.publish()
            self.assertFalse(any(path.endswith(("/reviews", "/merge")) for path, _, _ in self.calls))
            self.pr[field]["sha"] = original

    def test_failure_or_infrastructure_only_publishes_status(self):
        for environment in ({"VALIDATION_RESULT": "failure"}, {"AUTO_ELIGIBLE": "false"}):
            self.calls.clear()
            with patch.dict(os.environ, environment), patch.object(score_automation, "api", self.api):
                score_automation.publish()
            self.assertEqual(1, len(self.calls))
            self.assertTrue(self.calls[0][0].startswith("statuses/"))


if __name__ == "__main__":
    unittest.main()
