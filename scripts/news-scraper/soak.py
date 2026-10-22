"""Bounded final-release observations; never declares physical smoothness passed."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import socket
import subprocess
import time

from main import ROOT, atomic
from kiosk_probe import probe


HOST_COMMAND = (
    "cat /proc/sys/kernel/random/boot_id; "
    "systemctl --user show department-kiosk.service -p NRestarts -p ActiveState -p ActiveEnterTimestamp; "
    "ps -C chrome -o pid=,pcpu=,rss=; "
    "journalctl --user -u department-kiosk.service --since '5 minutes ago' --no-pager -n 30; "
    "journalctl -k --priority=warning --since '5 minutes ago' --no-pager -n 60"
)
CRASH = re.compile(r"RT_LINEAR_MISMATCH|segfault|Xorg.*SIGSEGV|Main process exited|Failed with result", re.I)


def listening(port=19223):
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=1):
            return True
    except OSError:
        return False


def assess(pages, previous, host, expected_version, minimum_news=1):
    """Pure acceptance signals. Connectivity and application faults stay distinct."""
    issues = []
    if {(p.get("width"), p.get("height")) for p in pages} != {(2560, 1440), (2048, 1152)} or len(pages) != 2:
        issues.append("display_targets_missing_or_duplicated")
    for page in pages:
        width = str(page.get("width", "unknown"))
        prior = next((p for p in previous.get("pages", []) if p.get("width") == page.get("width")), {})
        def add(code): issues.append(width + ":" + code)
        if page.get("assetVersion") != expected_version: add("wrong_release")
        if not isinstance(page.get("advanceCount"), int) or not isinstance(page.get("sinceAdvanceMs"), (int, float)):
            add("progress_telemetry_missing")
        elif page.get("sinceAdvanceMs", 0) > max(90000, (page.get("currentDuration") or 0) * 2):
            add("slide_progress_stalled")
        if prior.get("timeOrigin") is not None:
            if prior["timeOrigin"] != page.get("timeOrigin"):
                add("browser_reloaded")
            elif (isinstance(prior.get("advanceCount"), int) and isinstance(page.get("advanceCount"), int)
                  and page.get("observedAtMs", 0) - prior.get("observedAtMs", 0) > max(90000, (page.get("currentDuration") or 0) * 2)
                  and page["advanceCount"] <= prior["advanceCount"]):
                add("slide_progress_not_advanced")
        if page.get("paused") is not False: add("paused_or_uninitialized")
        if page.get("visibility") != "visible": add("page_hidden")
        if page.get("newsEnabled") is not True or (page.get("newsItems") or 0) < minimum_news:
            add("expected_news_missing")
        if page.get("errors") is None or page.get("unhandledRejections") is None:
            add("error_telemetry_missing")
        elif page["errors"] or page["unhandledRejections"]: add("javascript_errors")
    boot = re.search(r"^[a-f0-9-]{36}$", host, re.M)
    active = re.search(r"^ActiveEnterTimestamp=(.+)$", host, re.M)
    boot_id = boot[0] if boot else None
    service_started = active[1] if active else None
    if not boot_id: issues.append("boot_identity_missing")
    if "ActiveState=active" not in host: issues.append("kiosk_service_not_active")
    if previous.get("bootId") and previous["bootId"] != boot_id: issues.append("host_rebooted")
    if previous.get("serviceStartedAt") and previous["serviceStartedAt"] != service_started:
        issues.append("kiosk_service_restarted")
    if CRASH.search(host): issues.append("host_crash_evidence")
    return {"issues": issues, "bootId": boot_id, "serviceStartedAt": service_started}


def output_directory(value=None):
    scratch = (ROOT / "scratch").resolve()
    target = (Path(value) if value else scratch / ("soak-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"))).resolve()
    if target == scratch or not target.is_relative_to(scratch):
        raise ValueError("Soak output must be a new directory inside repository scratch")
    target.mkdir(parents=True, exist_ok=False)
    return target


def run(hours, output=None, interval=300, port=19223):
    target = output_directory(output)
    version = re.search(r'js/app\.js\?v=([^"\s]+)', (ROOT / "index.html").read_text(encoding="utf-8"))[1]
    revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    dirty = bool(subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True).strip())
    manifest = {"revision": revision, "dirty": dirty, "assetVersion": version,
                "startedAt": datetime.now(timezone.utc).isoformat(), "hours": hours, "intervalSeconds": interval, "localPort": port}
    atomic(target / "manifest.json", manifest)
    end = time.monotonic() + hours * 3600
    tunnel = None
    failures = observation_failures = count = 0
    previous = {}
    status_value = {"running": True, "samples": 0, "collectionFailures": 0,
                    "observationFailures": 0, "humanSmoothnessReview": "required", "output": str(target)}
    print(json.dumps({"output": str(target), **manifest}), flush=True)
    try:
        while True:
            record = {"at": datetime.now(timezone.utc).isoformat()}
            try:
                if not listening(port):
                    if tunnel:
                        tunnel.terminate()
                        tunnel.wait(timeout=10)
                    tunnel = subprocess.Popen(["ssh", "-N", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=yes", "-o", "ConnectTimeout=10",
                        "-o", "ExitOnForwardFailure=yes", "-o", "ServerAliveInterval=30", "-o", "ServerAliveCountMax=2",
                        "-L", f"127.0.0.1:{port}:127.0.0.1:9222", "mae-display"],
                        stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
                    time.sleep(3)
                record["pages"] = probe(port=port)
                result = subprocess.run(["ssh", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=yes", "-o", "ConnectTimeout=10", "mae-display", HOST_COMMAND],
                    capture_output=True, text=True, timeout=30,
                    creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
                record.update({"host": result.stdout[:32768], "sshExit": result.returncode})
                if result.returncode != 0:
                    failures += 1
                    record["collectionError"] = "host_ssh_failed"
                else:
                    record.update(assess(record["pages"], previous, record["host"], version))
                    if record["issues"]: observation_failures += 1
                    previous = record
            except Exception as exc:
                record["collectionError"] = type(exc).__name__
                failures += 1
            with (target / "samples.jsonl").open("a", encoding="utf-8") as stream:
                stream.write(json.dumps(record) + "\n")
            count += 1
            status_value.update({"running": time.monotonic() < end, "lastSample": record["at"], "samples": count,
                                 "collectionFailures": failures, "observationFailures": observation_failures,
                                 "observationStatus": "needs_review" if failures or observation_failures else "no_issues_observed"})
            atomic(target / "status.json", status_value)
            if time.monotonic() >= end: break
            time.sleep(min(interval, max(0, end - time.monotonic())))
    finally:
        if tunnel:
            tunnel.terminate()  # Never terminate a tunnel borrowed from another collector.
        status_value["running"] = False
        status_value["finishedAt"] = datetime.now(timezone.utc).isoformat()
        atomic(target / "status.json", status_value)
    return status_value


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--hours", type=float, default=24)
    p.add_argument("--output")
    p.add_argument("--interval", type=int, default=300)
    p.add_argument("--port", type=int, default=19223)
    a = p.parse_args()
    if not 0 < a.hours <= 24 or not 30 <= a.interval <= 300 or not 1024 <= a.port <= 65535:
        p.error("hours must be in (0,24]; interval in [30,300]; loopback port in [1024,65535]")
    run(a.hours, a.output, a.interval, a.port)
