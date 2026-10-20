"""Bounded CDN verification. No credentials are sent to the public site."""
import hashlib
import time
from urllib.request import urlopen
from main import ROOT

expected = hashlib.sha256((ROOT / "data/news.json").read_bytes()).hexdigest()
for attempt in range(10):
    try:
        with urlopen("https://airbreak404.github.io/department-display/data/news.json?t=" + str(time.time_ns()), timeout=15) as r:
            data = r.read(65537)
        if hashlib.sha256(data).hexdigest() == expected:
            print("Public news feed matches deployed revision.")
            break
    except OSError:
        pass
    if attempt == 9:
        raise SystemExit("Public feed did not match expected revision within verification window.")
    time.sleep(15)
