"""Build the downloadable catalogue from exported .qinscore files (Python 3)."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
entries = []
for path in sorted((ROOT / "scores").rglob("*.qinscore")):
    if path.stat().st_size > 4 * 1024 * 1024:
        raise ValueError(f"Score exceeds 4 MB: {path.name}")
    score = json.loads(path.read_text(encoding="utf-8-sig"))
    if score.get("format") != "qinbridge.score" or score.get("version") != 1:
        raise ValueError(f"Unsupported score format: {path.name}")
    if not isinstance(score.get("title"), str) or not score["title"].strip():
        raise ValueError(f"Missing title: {path.name}")
    if not isinstance(score.get("scoreText"), str) or not score["scoreText"].strip():
        raise ValueError(f"Missing score text: {path.name}")
    if not isinstance(score.get("settings"), dict):
        raise ValueError(f"Missing settings: {path.name}")
    relative = path.relative_to(ROOT).as_posix()
    language = path.relative_to(ROOT / "scores").parts[0]
    if language not in ("zh-CN", "en-US"):
        raise ValueError(f"Put the score in scores/zh-CN or scores/en-US: {relative}")
    entries.append({"id": relative, "title": score["title"], "file": relative, "language": language})
catalog = {"format": "qinbridge.catalog", "version": 1, "scores": entries}
(ROOT / "catalog.json").write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"Catalog updated: {len(entries)} scores")
