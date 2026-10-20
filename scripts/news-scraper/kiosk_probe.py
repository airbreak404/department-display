"""Read kiosk evidence over a localhost SSH-forwarded CDP connection.

Example tunnel: ssh -N -L 127.0.0.1:19222:127.0.0.1:9222 mae-display
This never changes browser flags or host services. --show-news briefly selects
the news page without changing pause/fullscreen state, for rollout screenshots.
"""
import argparse
import base64
import json
from pathlib import Path
import time

import requests
from websockets.sync.client import connect
from main import ROOT


def command(socket, method, params=None):
    command.counter += 1
    request_id = command.counter
    socket.send(json.dumps({"id": request_id, "method": method, "params": params or {}}))
    while True:
        result = json.loads(socket.recv(timeout=30))
        if result.get("id") == request_id:
            if "error" in result:
                raise RuntimeError(result["error"]["message"])
            return result.get("result", {})
command.counter = 0


EXPRESSION = """JSON.stringify({width:innerWidth,height:innerHeight,
paused:window.appSlideshow?.isPaused,index:window.appSlideshow?.currentIndex,
slides:window.appSlideshow?.slides.length,news:!!window.MaeNews,
newsEnabled:window.appSlideshow?.config.newsEnabled,
timeOrigin:performance.timeOrigin,
newsSummary:window.appSlideshow?.slides.find(s=>s.type==='mae-news')?.newsItems[0]?.summary,
newsCount:window.appSlideshow?.slides.filter(s=>s.type==='mae-news').length,
activeType:window.appSlideshow?.slides[window.appSlideshow?.currentIndex]?.type,
heap:performance.memory?.usedJSHeapSize,nodes:document.querySelectorAll('*').length,
visibility:document.visibilityState,fullscreen:!!document.fullscreenElement})"""


def probe(show_news=False, capture=False, frames=False):
    response = requests.get("http://127.0.0.1:19222/json/list", timeout=10)
    response.raise_for_status()
    results = []
    for index, page in enumerate(response.json()):
        if page.get("type") != "page" or not page["url"].startswith("https://airbreak404.github.io/department-display/"):
            continue
        url = page["webSocketDebuggerUrl"].replace(":9222/", ":19222/")
        with connect(url, open_timeout=10, max_size=16 * 1024 * 1024) as socket:
            if show_news:
                command(socket, "Runtime.evaluate", {"expression": "(() => {const s=window.appSlideshow;const i=s.slides.findIndex(x=>x.type==='mae-news');if(i>=0)s.showSlide(i);})()"})
                time.sleep(1)
            result = command(socket, "Runtime.evaluate", {"expression": EXPRESSION, "returnByValue": True})
            snapshot = json.loads(result["result"]["value"])
            if frames:
                result = command(socket, "Runtime.evaluate", {"expression": """new Promise(resolve=>{const times=[];let last;
                  const tick=t=>{if(last!==undefined)times.push(t-last);last=t;
                    if(times.length<120)requestAnimationFrame(tick);else resolve(JSON.stringify(times));};requestAnimationFrame(tick);})""",
                    "awaitPromise": True, "returnByValue": True})
                intervals = json.loads(result["result"]["value"])
                snapshot["frameMedianMs"] = sorted(intervals)[len(intervals) // 2]
                snapshot["frameP95Ms"] = sorted(intervals)[int(len(intervals) * .95)]
            if capture:
                image = command(socket, "Page.captureScreenshot", {"format": "png", "captureBeyondViewport": False})
                target = ROOT / "scratch/kiosk"
                target.mkdir(parents=True, exist_ok=True)
                path = target / f"page-{snapshot['width']}-{int(time.time())}.png"
                path.write_bytes(base64.b64decode(image["data"]))
                snapshot["screenshot"] = str(path)
            results.append(snapshot)
    return results


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--show-news", action="store_true")
    p.add_argument("--capture", action="store_true")
    p.add_argument("--frames", action="store_true")
    a = p.parse_args()
    print(json.dumps(probe(a.show_news, a.capture, a.frames), indent=2))
