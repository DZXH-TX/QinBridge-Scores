import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from validate_scores import validate_score
import build_catalog


def sample():
    return {
        "format": "qinbridge.score", "version": 3, "title": "MIDI protocol test", "sourceUrl": "", "scoreText": "",
        "settings": {"score": {"notation": "Midi", "timing": "SlashBeats"}},
        "midi": {
            "ticksPerQuarterNote": 480, "durationTicks": 1920,
            "notes": [{"pitch": 60, "tick": 120, "length": 480, "track": 0, "channel": 0, "velocity": 90}],
            "tempos": [{"tick": 0, "microsecondsPerQuarter": 500000}, {"tick": 960, "microsecondsPerQuarter": 600000}],
            "meters": [{"tick": 0, "numerator": 4, "denominator": 4}],
            "tracks": [{"index": 0, "name": "Piano"}], "selectedTracks": [0], "transposeSemitones": 0,
            "ignoredExpressionEvents": 0, "unpairedNoteEvents": 0,
        },
    }


def encode(value):
    return json.dumps(value).encode()


class MidiV3Tests(unittest.TestCase):
    def test_original_notes_rests_and_tempo_are_preserved(self):
        value = sample()
        self.assertEqual(value, validate_score(encode(value)))

    def test_versions_and_control_cannot_be_mixed(self):
        for change in ({"version": 1}, {"version": 2, "playbackControl": {"bpm": 80}},
                       {"playbackControl": None}, {"playbackControl": {"bpm": 80}}, {"midi": None}):
            value = sample()
            value.update(change)
            with self.subTest(change=change), self.assertRaises(ValueError):
                validate_score(encode(value))
        value = sample()
        del value["midi"]
        with self.assertRaises(ValueError):
            validate_score(encode(value))

    def test_typed_ranges_and_required_fields(self):
        for key, bad in (("ticksPerQuarterNote", True), ("ticksPerQuarterNote", 32768),
                         ("durationTicks", (1 << 40) + 1), ("durationTicks", 0),
                         ("transposeSemitones", 25), ("unpairedNoteEvents", -1),
                         ("ignoredExpressionEvents", "0"), ("selectedTracks", [True]),
                         ("selectedTracks", [1]), ("selectedTracks", [0, 0]),
                         ("notes", []), ("tracks", []), ("tempos", []), ("meters", [])):
            value = sample()
            value["midi"][key] = bad
            with self.subTest(key=key, bad=bad), self.assertRaises(ValueError):
                validate_score(encode(value))
        for key in ("ticksPerQuarterNote", "durationTicks", "notes", "tempos", "meters", "tracks", "selectedTracks"):
            value = sample()
            del value["midi"][key]
            with self.subTest(missing=key), self.assertRaises(ValueError):
                validate_score(encode(value))

    def test_note_bounds_and_playable_selection(self):
        for key, bad in (("pitch", 128), ("tick", -1), ("tick", 1920), ("length", 0), ("length", 1801),
                         ("track", 1), ("channel", 16), ("channel", 9), ("velocity", 0), ("velocity", True)):
            value = sample()
            value["midi"]["notes"][0][key] = bad
            with self.subTest(key=key, bad=bad), self.assertRaises(ValueError):
                validate_score(encode(value))

    def test_timing_maps_and_track_identity(self):
        for key, bad in (("tempos", [{"tick": 1, "microsecondsPerQuarter": 500000}]),
                         ("tempos", [{"tick": 0, "microsecondsPerQuarter": 0}]),
                         ("tempos", [{"tick": 0, "microsecondsPerQuarter": 500000}] * 2),
                         ("meters", [{"tick": 0, "numerator": 4, "denominator": 3}]),
                         ("tracks", [{"index": 0, "name": "A"}, {"index": 0, "name": "B"}])):
            value = sample()
            value["midi"][key] = bad
            with self.subTest(key=key), self.assertRaises(ValueError):
                validate_score(encode(value))

    def test_unknown_fields_are_rejected_at_each_depth(self):
        for location in ((), ("midi",), ("midi", "notes", 0), ("midi", "tempos", 0),
                         ("midi", "meters", 0), ("midi", "tracks", 0)):
            value = sample()
            target = value
            for key in location:
                target = target[key]
            target["execute"] = "untrusted"
            with self.subTest(location=location), self.assertRaises(ValueError):
                validate_score(encode(value))

    def test_midi_mode_is_required_and_not_available_to_text_scores(self):
        for notation, timing in (("Keyboard", "SlashBeats"), ("Midi", "SpaceGrid")):
            value = sample()
            value["settings"]["score"] = {"notation": notation, "timing": timing}
            with self.assertRaises(ValueError):
                validate_score(encode(value))
        value = sample()
        value.update(version=1, scoreText="A")
        del value["midi"]
        with self.assertRaises(ValueError):
            validate_score(encode(value))

    def test_note_budget_and_catalog_version(self):
        value = sample()
        value["midi"]["notes"] *= 100001
        with self.assertRaises(ValueError):
            validate_score(encode(value))
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "scores/en-US/midi.qinscore"
            path.parent.mkdir(parents=True)
            path.write_bytes(encode(sample()))
            with patch.object(build_catalog, "ROOT", root):
                build_catalog.main()
            catalog = json.loads((root / "catalog.json").read_text())
            self.assertEqual(1, catalog["version"])
            self.assertEqual(sample()["title"], catalog["scores"][0]["title"])


if __name__ == "__main__":
    unittest.main()
