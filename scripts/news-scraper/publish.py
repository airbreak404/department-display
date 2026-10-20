"""Validate and move the two permitted ingestion outputs across the job boundary."""
import argparse
from datetime import datetime, timezone
from pathlib import Path
import shutil
from main import ROOT, atomic, read
from news import validate_feed


def prepare():
    target = ROOT / "scratch/publish"
    target.mkdir(parents=True, exist_ok=True)
    for source, name in (("data/news.json", "news.json"), ("scripts/news-scraper/state.json", "state.json")):
        shutil.copyfile(ROOT / source, target / name)


def apply(source):
    source = Path(source)
    if {p.name for p in source.iterdir()} != {"news.json", "state.json"}:
        raise ValueError("unexpected_artifact_files")
    for path in source.iterdir():
        if path.is_symlink() or not path.is_file() or path.stat().st_size > 1024 * 1024:
            raise ValueError("artifact_bounds")
    feed = validate_feed(read(source / "news.json", None), datetime.now(timezone.utc))
    state = read(source / "state.json", None)
    if not isinstance(state, dict) or state.get("version") != 1 or not isinstance(state.get("decisions"), dict):
        raise ValueError("state_schema")
    atomic(ROOT / "data/news.json", feed)
    atomic(ROOT / "scripts/news-scraper/state.json", state)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("mode", choices=("prepare", "apply"))
    p.add_argument("--source", default="scratch/download")
    a = p.parse_args()
    prepare() if a.mode == "prepare" else apply(a.source)
