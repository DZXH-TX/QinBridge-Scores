"""Validate score data only. Never import, check out, or execute candidate files."""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
import json
import math
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
SCORE_BYTES = 4 * 1024 * 1024
CATALOG_BYTES = 1024 * 1024
SOURCE_BYTES = 64 * 1024
SOURCE_SUFFIX = ".source.json"
MAX_SCORES = 2000
TOTAL_BYTES = 64 * 1024 * 1024
KEYS = "ZXCVBNMASDFGHJQWERTYU"
SHA = re.compile(r"[0-9a-f]{40}\Z")
HEADER = re.compile(r"BPM\s*[:=]\s*(\d+(?:\.\d+)?)\s*(?:(\d+)\s*/\s*(\d+)\s*拍?)?\s*", re.I)
HEADING = re.compile(r"[\s—\-:]*(?:键盘|按键|电脑|数字|手机)(?:琴谱|棋谱|谱)?[\s—\-:]*")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def strict_json(raw, maximum):
    require(len(raw) <= maximum, "JSON exceeds byte limit")
    text = raw.decode("utf-8-sig", errors="strict")
    depth = 0
    quoted = escaped = False
    for char in text:
        if quoted:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                quoted = False
        elif char == '"':
            quoted = True
        elif char in "[{":
            depth += 1
            require(depth <= 12, "JSON nesting exceeds 12")
        elif char in "]}":
            depth -= 1

    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, "Duplicate JSON key: " + key)
            result[key] = value
        return result

    def number(value, converter):
        require(len(value) <= 32, "JSON number is too long")
        result = converter(value)
        require(math.isfinite(result), "Non-finite JSON number")
        return result

    def invalid(value):
        raise ValueError("Invalid JSON constant: " + value)

    return json.loads(text, object_pairs_hook=pairs, parse_constant=invalid,
                      parse_int=lambda v: number(v, int), parse_float=lambda v: number(v, float))


def shape(value, allowed, required=()):
    require(type(value) is dict, "Expected a JSON object")
    require(not (value.keys() - set(allowed)), "Unknown JSON fields: " + repr(sorted(value.keys() - set(allowed))))
    require(set(required) <= value.keys(), "Missing required JSON fields")


def text_field(value, limit, empty=False):
    require(type(value) is str and len(value) <= limit, "Invalid or oversized text field")
    require(empty or bool(value.strip()), "Empty text field")
    require(not any(ord(c) < 32 or 0xD800 <= ord(c) <= 0xDFFF or c in "\u202a\u202b\u202c\u202d\u202e\u2066\u2067\u2068\u2069" for c in value),
            "Control characters are not allowed in metadata")


def bounded_number(value, minimum, maximum):
    require(type(value) in (int, float) and math.isfinite(value) and minimum <= value <= maximum,
            "Number outside permitted range")


def source_url(value):
    text_field(value, 2048, empty=True)
    if value:
        url = urlsplit(value)
        require(url.scheme in ("http", "https") and bool(url.hostname) and not url.username and not url.password,
                "Source must be an HTTP(S) URL")


def validate_source_note(raw):
    """Read optional provenance as inert data; do not require or verify a license."""
    note = strict_json(raw, SOURCE_BYTES)
    limits = {"sourceUrl": 2048, "sourceTitle": 256, "author": 256,
              "credit": 2048, "license": 2048, "notes": 4096}
    shape(note, limits)
    for key, value in note.items():
        text_field(value, limits[key], empty=True)
    source_url(note.get("sourceUrl", ""))
    return note


def score_path(path):
    text_field(path, 512)
    parts = path.split("/")
    require(len(parts) == 3 and parts[0] == "scores" and parts[1] in ("zh-CN", "en-US"), "Invalid score directory")
    name = parts[2]
    require(name.endswith(".qinscore") and not name.startswith(".") and len(name) > 9
            and not any(c in path for c in '\\:*?"<>|'), "Invalid score filename")
    return parts[1]


def validate_notation(text, notation, timing, ignore_measures):
    require(type(text) is str and 0 < len(text) <= 1_000_000, "Invalid score text length")
    normalized = text.replace("\r\n", "\n").replace("\r", "\n").replace("\t", "    ")
    normalized = normalized.translate(str.maketrans("（［【）］】／＋－：０１２３４５６７８９\u00a0\u202f\u3000", "([[)]]/+-:0123456789   ")).replace("\u200b", "").replace("\ufeff", "")
    lines = []
    for line in normalized.split("\n"):
        trimmed = line.strip()
        if not trimmed or HEADING.fullmatch(trimmed):
            continue
        if trimmed.upper().startswith("BPM"):
            require(len(trimmed) <= 120, "Oversized BPM header")
            header = HEADER.fullmatch(trimmed)
            require(header is not None, "Invalid BPM header")
            bounded_number(float(header[1]), 1, 1000)
            if header[2]:
                bounded_number(int(header[2]), 1, 12)
                require(int(header[3]) in (2, 4, 8, 16), "Invalid header beat unit")
            continue
        if ignore_measures:
            line = re.sub(r"/\s*\d+\s*$", "/", line)
        lines.append(line)
    if notation == "Auto":
        notation = "Keyboard" if any(re.search("[A-Za-z]", line) for line in lines) else "Numbers"
    notes = work = 0
    for line in lines:
        stack = []
        i = 0
        while i < len(line):
            char = line[i]
            i += 1
            if char == " ":
                continue
            if char in "/|" or char == "0" or (char == "-" and notation == "Keyboard"):
                require(not stack, "Rest or separator inside a note group")
                continue
            if char in "([":
                require(len(stack) < 32, "Note group nesting exceeds 32")
                stack.append((char, []))
                continue
            if char in ")]":
                require(bool(stack), "Unmatched closing bracket")
                opening, children = stack.pop()
                require(char == (")" if opening == "(" else "]") and bool(children), "Mismatched or empty note group")
                work += sum(len(child) for child in children)
                require(work <= 2_000_000, "Note group expansion exceeds budget")
                if opening == "[":
                    groups = [mask for child in children for mask in child]
                else:
                    groups = [0] * max(map(len, children))
                    for child in children:
                        for step, mask in enumerate(child):
                            require(not groups[step] & mask, "Duplicate simultaneous note")
                            groups[step] |= mask
                if stack:
                    stack[-1][1].append(groups)
                continue
            if notation == "Keyboard":
                require(len(char.upper()) == 1 and char.upper() in KEYS, "Invalid keyboard note")
                note = KEYS.index(char.upper())
            else:
                octave = 1
                if char in "+-":
                    octave = 2 if char == "+" else 0
                    require(i < len(line), "Missing note after octave prefix")
                    char = line[i]
                    i += 1
                require(char in "1234567", "Invalid numeric note")
                note = octave * 7 + int(char) - 1
            notes += 1
            require(notes <= 100_000, "Score exceeds 100000 notes")
            if stack:
                stack[-1][1].append([1 << note])
        require(not stack, "Unclosed note group")
    require(notes > 0, "Score contains no notes")


def validate_score(raw):
    score = strict_json(raw, SCORE_BYTES)
    shape(score, ("format", "version", "title", "sourceUrl", "scoreText", "settings"),
          ("format", "version", "title", "scoreText", "settings"))
    require(score["format"] == "qinbridge.score" and type(score["version"]) is int and score["version"] == 1, "Unsupported score format/version")
    text_field(score["title"], 256)
    source_url(score.get("sourceUrl", ""))
    settings = score["settings"]
    shape(settings, ("slotMilliseconds", "arpeggioMilliseconds", "gate", "rhythm", "score", "minimumTriggerIntervalMilliseconds"))
    bounded_number(settings.get("slotMilliseconds", 125), 20, 2000)
    bounded_number(settings.get("arpeggioMilliseconds", 18), 1, 100)
    bounded_number(settings.get("gate", .72), .1, .95)
    bounded_number(settings.get("minimumTriggerIntervalMilliseconds", 150), 30, 300)
    rhythm = settings.get("rhythm")
    if rhythm is not None:
        shape(rhythm, ("bpm", "beatsPerBar", "beatUnit", "unitsPerBeat"))
        bpm, beats, unit, divisions = (rhythm.get(k, v) for k, v in (("bpm", 120), ("beatsPerBar", 4), ("beatUnit", 4), ("unitsPerBeat", 4)))
        bounded_number(bpm, 1, 1000)
        require(type(beats) is int and 1 <= beats <= 12, "Invalid beats per bar")
        require(type(unit) is int and unit in (2, 4, 8, 16), "Invalid beat unit")
        require(type(divisions) is int and divisions in (1, 2, 3, 4, 6, 8), "Invalid subdivisions")
        bounded_number(60000 / bpm / divisions, 20, 2000)
    options = settings.get("score")
    if options is None:
        options = {"notation": "Keyboard"}
    shape(options, ("notation", "timing", "ignoreMeasureNumbers"))
    notation, timing, ignore = options.get("notation", "Auto"), options.get("timing", "SpaceGrid"), options.get("ignoreMeasureNumbers", False)
    require(notation in ("Auto", "Keyboard", "Numbers") and timing in ("SpaceGrid", "SlashBeats") and type(ignore) is bool, "Invalid score reading options")
    validate_notation(score["scoreText"], notation, timing, ignore)
    return score


def git(*args, root=ROOT):
    return subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True, timeout=90).stdout


def tree(ref, root=ROOT):
    require(SHA.fullmatch(ref) is not None, "Expected a full commit SHA")
    entries = {}
    for record in git("ls-tree", "-r", "-z", "-l", "--full-tree", ref, root=root).split(b"\0"):
        if not record:
            continue
        metadata, path = record.split(b"\t", 1)
        mode, kind, oid, size = metadata.split()
        entries[path.decode("utf-8", errors="strict")] = (mode.decode(), kind.decode(), oid.decode(), int(size) if size != b"-" else -1)
    require(len(entries) <= 5000, "Repository file count exceeds limit")
    return entries


def _validate_blob(item):
    root, path, oid = item
    try:
        raw = git("cat-file", "blob", oid, root=root)
        if path.endswith(SOURCE_SUFFIX):
            validate_source_note(raw)
            return path, None
        return path, validate_score(raw)["title"]
    except (ValueError, UnicodeError) as error:
        raise ValueError(repr(path) + ": " + str(error)) from error


def validate_repository(ref, base=None, root=ROOT, workers=4):
    require(1 <= workers <= 4, "Worker count must be between 1 and 4")
    entries = tree(ref, root)
    require("catalog.json" in entries, "Missing catalog.json")
    data_paths = sorted(path for path in entries if path.startswith("scores/") and path != "scores/.gitkeep")
    sources = [path for path in data_paths if path.endswith(SOURCE_SUFFIX)]
    scores = [path for path in data_paths if not path.endswith(SOURCE_SUFFIX)]
    require(len(scores) <= MAX_SCORES, "Too many scores")
    for path in sources:
        score_path(path.removesuffix(SOURCE_SUFFIX))
        require(path.removesuffix(SOURCE_SUFFIX) in scores, "Source note must accompany an existing score")
    total = 0
    for path in ["catalog.json", *data_paths]:
        if path != "catalog.json":
            score_path(path.removesuffix(SOURCE_SUFFIX))
        mode, kind, _, size = entries[path]
        require(mode == "100644" and kind == "blob", "Score data must be regular non-executable files")
        maximum = CATALOG_BYTES if path == "catalog.json" else SOURCE_BYTES if path.endswith(SOURCE_SUFFIX) else SCORE_BYTES
        require(0 <= size <= maximum, "File exceeds byte limit")
        total += size
    require(total <= TOTAL_BYTES, "Catalogue exceeds total byte budget")
    catalog = strict_json(git("cat-file", "blob", entries["catalog.json"][2], root=root), CATALOG_BYTES)
    shape(catalog, ("format", "version", "scores"), ("format", "version", "scores"))
    require(catalog["format"] == "qinbridge.catalog" and type(catalog["version"]) is int and catalog["version"] == 1, "Unsupported catalogue format/version")
    require(type(catalog["scores"]) is list and len(catalog["scores"]) <= MAX_SCORES, "Invalid catalogue entries")
    jobs = [(str(root), path, entries[path][2]) for path in data_paths]
    if workers == 1:
        parsed = list(map(_validate_blob, jobs))
    else:
        with ProcessPoolExecutor(max_workers=workers) as pool:
            parsed = list(pool.map(_validate_blob, jobs, chunksize=1))
    expected = [{"id": path, "title": title, "file": path, "language": score_path(path)} for path, title in parsed if title is not None]
    require(catalog["scores"] == expected, "Catalogue must exactly match the sorted score files, titles, IDs, and languages; run tools/build_catalog.py")
    data_only = False
    if base:
        before = tree(base, root)
        changed = {path for path in entries.keys() | before.keys() if entries.get(path) != before.get(path)}
        data_only = 0 < len(changed) <= 200
        for path in changed:
            if path != "catalog.json" and data_only:
                try:
                    score_path(path.removesuffix(SOURCE_SUFFIX))
                except ValueError:
                    data_only = False
    return {"scores": len(scores), "source_notes": len(sources), "bytes": total, "data_only": data_only}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ref", default=None)
    parser.add_argument("--base")
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    ref = args.ref or git("rev-parse", "HEAD").decode().strip()
    try:
        print(json.dumps(validate_repository(ref, args.base, workers=args.workers)))
    except (ValueError, OSError, subprocess.SubprocessError) as error:
        print("Validation failed: " + json.dumps(str(error), ensure_ascii=True), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
