"""Prepare and verify the Chinese-only public mirror; credentials are handled by CI."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from urllib.parse import quote, urlsplit
from urllib.request import urlopen

sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate_scores import ROOT, SCORE_BYTES, CATALOG_BYTES, MAX_SCORES, TOTAL_BYTES, require, score_path, validate_score


def build(source: Path, output: Path) -> int:
    require(not output.exists(), "Output directory must not exist; use a fresh staging directory")
    directory = source / "scores" / "zh-CN"
    require(not directory.is_symlink() and not directory.parent.is_symlink(), "Symlinks are not allowed")
    entries, files = [], []
    total = 0
    # Sidecar provenance, English scores and repository code are intentionally outside this selection.
    for path in sorted(directory.glob("*.qinscore")):
        require(not path.is_symlink() and path.is_file(), "Scores must be regular files")
        relative = path.relative_to(source).as_posix()
        require(score_path(relative) == "zh-CN", "Only Chinese scores may enter the mirror")
        with path.open("rb") as stream:
            raw = stream.read(SCORE_BYTES + 1)
        total += len(raw)
        require(total <= TOTAL_BYTES and len(entries) < MAX_SCORES, "Mirror exceeds resource limits")
        score = validate_score(raw)
        entries.append({"id": relative, "title": score["title"], "file": relative, "language": "zh-CN"})
        files.append((relative, raw))
    catalog = (json.dumps({"format": "qinbridge.catalog", "version": 1, "scores": entries},
                          ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    require(len(catalog) <= CATALOG_BYTES and total + len(catalog) <= TOTAL_BYTES, "Mirror exceeds byte limit")
    # Validate every score before writing any uploadable output.
    (output / "scores" / "zh-CN").mkdir(parents=True)
    for relative, raw in files:
        (output / relative).write_bytes(raw)
    (output / "catalog.json").write_bytes(catalog)
    return len(entries)


def verify(output: Path, base_url: str) -> int:
    uri = urlsplit(base_url)
    require(uri.scheme == "https" and uri.hostname and not uri.username and not uri.password
            and not uri.query and not uri.fragment, "Verification requires an HTTPS mirror root")
    catalog_raw = (output / "catalog.json").read_bytes()
    catalog = json.loads(catalog_raw)
    paths = ["catalog.json", *(entry["file"] for entry in catalog["scores"])]
    for relative in paths:
        if relative != "catalog.json":
            require(score_path(relative) == "zh-CN", "Unexpected verification path")
        expected = (output / relative).read_bytes()
        url = base_url.rstrip("/") + "/" + quote(relative, safe="/")
        with urlopen(url, timeout=30) as response:
            actual = response.read(len(expected) + 1)
        require(actual == expected, "Public mirror differs from the validated payload: " + relative)
    return len(catalog["scores"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--verify-url", help="Verify a previously prepared payload against its public mirror")
    args = parser.parse_args()
    if args.verify_url:
        count = verify(args.output, args.verify_url)
        print(f"Verified {count} Chinese scores and the Chinese catalog through public HTTPS")
    else:
        count = build(ROOT, args.output)
        print(f"Prepared {count} Chinese scores and one catalog; no English scores or source notes")


if __name__ == "__main__":
    main()
