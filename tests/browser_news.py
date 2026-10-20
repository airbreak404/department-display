"""Real Chromium regression checks and screenshots; no live external services needed."""
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import threading

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "test-results"
NOW = datetime.now(timezone.utc)


def feed(count):
    return {"schemaVersion": 1, "contentUpdatedAt": NOW.strftime("%Y-%m-%dT%H:%M:%SZ"), "items": [
        {"id": f"{i + 1:024x}", "title": 'MAE research & engineering: "Students build the future" ' + ('long headline ' * 8 if i == 0 else str(i)),
         "summary": "Mechanical and aerospace engineering students explore propulsion, robotics, and sustainable transportation. " * 2,
         "url": f"https://wmich.edu/engineer/news/2026/10/story-{i}",
         "publishedDate": (NOW - timedelta(days=1)).date().isoformat(),
         "source": "WMU College of Engineering and Applied Sciences", "expiresAt": (NOW + timedelta(days=10)).strftime("%Y-%m-%dT%H:%M:%SZ")}
        for i in range(count)]}


class Handler(SimpleHTTPRequestHandler):
    def log_message(self, *_): pass


def run():
    OUT.mkdir(exist_ok=True)
    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(Handler, directory=str(ROOT)))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with sync_playwright() as p:
            options = {"headless": True}
            # Use installed browser on this Windows workstation; CI installs its matching revision.
            if os.name == "nt":
                installed = list((Path(os.environ["LOCALAPPDATA"]) / "ms-playwright").glob("chromium-*/chrome-win*/chrome.exe"))
                if installed: options["executable_path"] = str(sorted(installed)[-1])
            browser = p.chromium.launch(**options)
            page = browser.new_page(viewport={"width": 2048, "height": 1152})
            errors = []
            page.on("pageerror", lambda e: errors.append(str(e)))
            current = {"feed": feed(3), "bad": False, "missing": False}
            base_fixture = json.loads((ROOT / 'data/slides.json').read_text(encoding='utf-8'))
            base_fixture['config']['newsEnabled'] = True
            page.route("**/data/slides.json?*", lambda r: r.fulfill(content_type="application/json", body=json.dumps(base_fixture)))
            page.route("**/data/news.json?*", lambda r: r.fulfill(status=404 if current["missing"] else 200,
                content_type="application/json", body="{" if current["bad"] else json.dumps(current["feed"])))
            page.route("https://api.open-meteo.com/**", lambda r: r.abort())
            page.route("https://api.qrserver.com/**", lambda r: r.abort())
            page.goto(f"http://127.0.0.1:{server.server_port}/?pause=1")
            page.wait_for_function("() => window.appSlideshow && window.appSlideshow.slides.some(s => s.type === 'mae-news')")
            fixture = feed(8)
            result = page.evaluate("""f => {
              const base = {config:{},slides:[{id:'base',type:'hero'},{id:'way',type:'wayfinding'}]};
              const original=JSON.stringify(base);
              for(let n=0;n<=8;n++) {
                const feed={...f,items:f.items.slice(0,n)};
                const first=MaeNews.compose(base,feed), second=MaeNews.compose(first,feed);
                if(first.slides.filter(s=>s.type==='mae-news').length !== Math.ceil(n/3)) throw Error('page count '+n);
                if(JSON.stringify(first)!==JSON.stringify(second)) throw Error('duplicate injection');
              }
              if(JSON.stringify(base)!==original) throw Error('mutated fallback');
              if(MaeNews.compose({...base,config:{newsEnabled:false}},f).slides.length!==2) throw Error('disable flag');
              const bad=JSON.parse(JSON.stringify(f)); bad.items[0].title='<script>alert(1)</script>';
              if(MaeNews.validate(bad).items.length!==7) throw Error('markup accepted');
              const expired=JSON.parse(JSON.stringify(f)); expired.items[0].expiresAt='2020-01-01T00:00:00Z';
              if(MaeNews.validate(expired).items.length!==7) throw Error('expiry');
              const dup={...f,items:[f.items[0],f.items[0]]};
              if(MaeNews.validate(dup).items.length!==1) throw Error('duplicate ids');
              if(MaeNews.formatDate('2026-10-05')!=='Oct 5, 2026') throw Error('date shift');
              try { MaeNews.validate({...f,schemaVersion:2}); throw Error('schema accepted'); }
              catch(e) { if(e.message==='schema accepted') throw e; }
              return true;
            }""", fixture)
            assert result
            for count in (1, 2, 3, 8):
                page.evaluate("""f => { const s=appSlideshow; const base={config:s.config,slides:s.slides.filter(x=>x.type!=='mae-news')};
                  s.queueData(MaeNews.compose(base,f)); s.showSlide(s.slides.findIndex(x=>x.type==='mae-news')); }""", feed(count))
                page.wait_for_timeout(500)
                for width, height in ((2048, 1152), (2560, 1440)):
                    page.set_viewport_size({"width": width, "height": height})
                    page.screenshot(path=str(OUT / f"news-{count}-{width}.png"))
                    assert page.evaluate("""() => [...document.querySelectorAll('.slide.active .news-card')].every(e => {
                      const r=e.getBoundingClientRect(), p=document.querySelector('.slides-viewport').getBoundingClientRect();
                      return r.left>=p.left-1 && r.right<=p.right+1 && r.bottom<=p.bottom+1 && r.top>=p.top-1;
                    })"""), "Card outside slide canvas"
            # Source text is encoded exactly once, and each engine rebuild retains pause.
            assert page.locator('.slide.active h2').first.inner_text().startswith('MAE research & engineering: "')
            assert page.evaluate("appSlideshow.isPaused")
            current["feed"] = feed(1)
            page.evaluate("document.dispatchEvent(new Event('visibilitychange'))")
            page.wait_for_function("() => appSlideshow.slides.filter(s=>s.type==='mae-news').length===1")
            for kind in ("bad", "missing"):
                current[kind] = True
                page.evaluate("document.dispatchEvent(new Event('visibilitychange'))")
                page.wait_for_timeout(500)
                assert page.evaluate("appSlideshow.slides.some(s=>s.type==='mae-news')"), "Lost retained news"
                current[kind] = False
            current["feed"] = feed(0)
            page.evaluate("document.dispatchEvent(new Event('visibilitychange'))")
            page.wait_for_function("() => !appSlideshow.slides.some(s=>s.type==='mae-news')")
            # Running updates wait for a boundary and preserve stable base-slide identity.
            assert page.evaluate("""f => { const s=appSlideshow; s.isPaused=false;
              s.beforeAdvance=null; // Isolate engine boundary semantics from app-owned source data.
              const data=MaeNews.compose({config:s.config,slides:s.slides},f);
              const old=s.slides.length; s.queueData(data);
              if(s.slides.length!==old) return false;
              s.nextSlide(); return s.slides.length>old && !s.pendingData;
            }""", feed(2))
            assert not errors, errors
            offline = browser.new_page(viewport={"width": 2048, "height": 1152})
            offline.route("**/data/*.json?*", lambda r: r.abort())
            offline.route("https://**", lambda r: r.abort())
            offline.goto(f"http://127.0.0.1:{server.server_port}/?pause=1")
            offline.wait_for_function("() => window.appSlideshow && appSlideshow.slides.length > 0")
            assert offline.evaluate("!appSlideshow.slides.some(s=>s.type==='mae-news')"), 'Offline startup fabricated news'
            offline.close()
            browser.close()
            print("Chromium news regression checks passed; screenshots in test-results/.")
    finally:
        server.shutdown()
        server.server_close()


if __name__ == '__main__': run()
