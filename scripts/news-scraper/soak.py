"""Bounded 24-hour evidence collection; no host/browser configuration changes.

Uses existing SSH credentials and a dedicated loopback CDP tunnel, records every
five minutes, and exits after the selected duration. This collects evidence;
operator-visible smoothness still requires human review.
"""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import socket
import subprocess
import time

from main import ROOT
from kiosk_probe import probe


def listening():
    try:
        with socket.create_connection(("127.0.0.1", 19222), timeout=1):
            return True
    except OSError:
        return False


def run(hours):
    target = ROOT / "scratch/soak"
    target.mkdir(parents=True, exist_ok=True)
    end = time.monotonic() + hours * 3600
    tunnel = None
    failures = 0
    count = 0
    try:
        while True:
            record = {"at": datetime.now(timezone.utc).isoformat()}
            try:
                if not listening():
                    if tunnel: tunnel.terminate()
                    tunnel = subprocess.Popen(["ssh", "-N", "-o", "BatchMode=yes", "-o", "ConnectTimeout=10",
                        "-o", "ExitOnForwardFailure=yes", "-o", "ServerAliveInterval=30",
                        "-L", "127.0.0.1:19222:127.0.0.1:9222", "mae-display"],
                        stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
                    time.sleep(3)
                record["pages"] = probe()
                status = subprocess.run(["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=10", "mae-display",
                    "systemctl --user show department-kiosk.service -p NRestarts -p ActiveState -p ActiveEnterTimestamp; "
                    "ps -C chrome -o pid=,pcpu=,rss=; "
                    "journalctl --user -u department-kiosk.service --since '5 minutes ago' --no-pager -n 30"],
                    capture_output=True, text=True, timeout=30,
                    creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
                record["host"] = status.stdout
                record["sshExit"] = status.returncode
                if len(record["pages"]) != 2 or status.returncode != 0:
                    failures += 1
            except Exception as exc:
                record["error"] = type(exc).__name__
                failures += 1
            with (target / "samples.jsonl").open("a", encoding="utf-8") as stream:
                stream.write(json.dumps(record) + "\n")
            count += 1
            (target / "status.json").write_text(json.dumps({"running": time.monotonic() < end,
                "lastSample": record["at"], "samples": count, "collectionFailures": failures,
                "humanSmoothnessReview": "required"}, indent=2), encoding="utf-8")
            if time.monotonic() >= end:
                break
            time.sleep(min(300, max(0, end - time.monotonic())))
    finally:
        if tunnel: tunnel.terminate()


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--hours", type=float, default=24)
    a = p.parse_args()
    if not 0 < a.hours <= 24:
        p.error("hours must be greater than zero and no more than 24")
    run(a.hours)
