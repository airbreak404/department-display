"""Allowlist public assets. Review/state files never enter the Pages artifact."""
from datetime import datetime, timezone
import hashlib
import shutil
from main import ROOT, read
from news import validate_feed
from health import validate as validate_health


def build():
    validate_feed(read(ROOT / "data/news.json", None), datetime.now(timezone.utc))
    health = ROOT / "data/news-health.json"
    if health.exists():
        validate_health(read(health, None))
    target = ROOT / "scratch/site"
    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True)
    for name in ("css", "js", "images"):
        shutil.copytree(ROOT / name, target / name)
    (target / "data").mkdir()
    for name in ("slides.json", "fallback.js", "news.json"):
        shutil.copyfile(ROOT / "data" / name, target / "data" / name)
    if health.exists():
        shutil.copyfile(health, target / "data/news-health.json")
    shutil.copyfile(ROOT / "index.html", target / "index.html")
    (target / ".nojekyll").touch()
    print("feed_sha256=" + hashlib.sha256((target / "data/news.json").read_bytes()).hexdigest())


if __name__ == "__main__":
    build()
