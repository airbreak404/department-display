"""Validate and move the two permitted ingestion outputs across the job boundary."""
import argparse
from datetime import datetime, timezone
from pathlib import Path
import shutil
from main import ROOT, atomic, read
from news import validate_feed
from state import validate as validate_state
from health import validate as validate_health


def prepare():
    target = ROOT / "scratch/publish"
    target.mkdir(parents=True, exist_ok=True)
    for source, name in (("data/news.json", "news.json"), ("scripts/news-scraper/state.json", "state.json"),
                         ("data/news-health.json", "news-health.json")):
        shutil.copyfile(ROOT / source, target / name)


def apply(source):
    source = Path(source)
    if {p.name for p in source.iterdir()} != {"news.json", "state.json", "news-health.json"}:
        raise ValueError("unexpected_artifact_files")
    for path in source.iterdir():
        if path.is_symlink() or not path.is_file() or path.stat().st_size > 1024 * 1024:
            raise ValueError("artifact_bounds")
    feed = validate_feed(read(source / "news.json", None), datetime.now(timezone.utc))
    state = validate_state(read(source / "state.json", None))
    health = validate_health(read(source / "news-health.json", None))
    atomic(ROOT / "data/news.json", feed)
    atomic(ROOT / "scripts/news-scraper/state.json", state)
    atomic(ROOT / "data/news-health.json", health)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("mode", choices=("prepare", "apply"))
    p.add_argument("--source", default="scratch/download")
    a = p.parse_args()
    prepare() if a.mode == "prepare" else apply(a.source)
