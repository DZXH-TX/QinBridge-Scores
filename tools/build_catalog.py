"""Build catalog.json only after all local score files pass data validation."""
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate_scores import ROOT, SCORE_BYTES, CATALOG_BYTES, MAX_SCORES, TOTAL_BYTES, require, score_path, validate_score


def main():
    entries = []
    total = 0
    for path in sorted((ROOT / "scores").rglob("*.qinscore")):
        relative = path.relative_to(ROOT).as_posix()
        language = score_path(relative)
        require(not any(part.is_symlink() for part in [path, *path.parents] if part != ROOT), "Symlinks are not allowed")
        with path.open("rb") as stream:
            raw = stream.read(SCORE_BYTES + 1)
        total += len(raw)
        require(total <= TOTAL_BYTES and len(entries) < MAX_SCORES, "Catalogue exceeds resource limits")
        score = validate_score(raw)
        entries.append({"id": relative, "title": score["title"], "file": relative, "language": language})
    output = (json.dumps({"format": "qinbridge.catalog", "version": 1, "scores": entries}, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    require(len(output) <= CATALOG_BYTES and total + len(output) <= TOTAL_BYTES, "Catalogue exceeds byte limit")
    (ROOT / "catalog.json").write_bytes(output)
    print(f"Catalog updated: {len(entries)} validated scores")


if __name__ == "__main__":
    main()
