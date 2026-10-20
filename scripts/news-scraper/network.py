"""Bounded, same-publisher HTTP access. Never fetch arbitrary model/source URLs."""
import ipaddress
import socket
import time
from urllib.parse import urljoin, urlsplit
from urllib.robotparser import RobotFileParser

import requests

HOSTS = frozenset({"wmich.edu"})
LIMIT = 2 * 1024 * 1024
AGENT = "WMU-MAE-News/1.0"


class FetchError(Exception):
    def __init__(self, kind):
        super().__init__(kind)  # Do not expose request URLs, bodies, or credentials.
        self.kind = kind


def safe_url(url, resolve=True):
    try:
        parts = urlsplit(url)
        if (parts.scheme != "https" or parts.hostname not in HOSTS or
                parts.username or parts.password or parts.port not in (None, 443)):
            raise ValueError()
        if resolve:
            addresses = socket.getaddrinfo(parts.hostname, 443, type=socket.SOCK_STREAM)
            if not addresses or any(not ipaddress.ip_address(a[4][0]).is_global for a in addresses):
                raise ValueError()
    except (ValueError, OSError):
        raise FetchError("unsafe_destination") from None
    return url


class Client:
    def __init__(self, session=None, sleep=time.sleep):
        self.session = session or requests.Session()
        self.session.trust_env = False
        self.session.headers.update({"User-Agent": AGENT, "Accept": "text/html"})
        self.sleep = sleep
        self.robots = {}

    def _get(self, url):
        for redirects in range(4):
            safe_url(url)
            response = None
            for attempt in range(3):
                try:
                    response = self.session.get(url, timeout=(5, 20), stream=True,
                                                allow_redirects=False)
                except requests.RequestException:
                    if attempt == 2:
                        raise FetchError("network") from None
                    self.sleep(2 ** attempt)
                    continue
                if response.status_code not in (429, 500, 502, 503, 504):
                    break
                retry = response.headers.get("Retry-After", "")
                delay = min(int(retry), 30) if retry.isdigit() else 2 ** attempt
                response.close()
                if attempt == 2:
                    raise FetchError("rate_or_server_error")
                self.sleep(delay)
            if response.status_code in (301, 302, 303, 307, 308):
                destination = urljoin(url, response.headers.get("Location", ""))
                response.close()
                if redirects == 3:
                    raise FetchError("redirect_limit")
                safe_url(destination)
                url = destination
                continue
            try:
                if response.status_code == 404:
                    raise FetchError("not_found")
                if response.status_code != 200:
                    raise FetchError("http_error")
                if response.headers.get("Content-Type", "").split(";")[0].lower() not in (
                        "text/html", "application/xhtml+xml", "text/plain"):
                    raise FetchError("content_type")
                content = bytearray()
                for chunk in response.iter_content(16384):
                    content.extend(chunk)
                    if len(content) > LIMIT:
                        raise FetchError("response_too_large")
                return bytes(content)
            except requests.RequestException:
                raise FetchError("read_error") from None
            finally:
                response.close()
        raise FetchError("redirect_limit")

    def get(self, url):
        safe_url(url)
        origin = "https://" + urlsplit(url).hostname
        if origin not in self.robots:
            # Missing robots permits access; other failures fail closed.
            parser = RobotFileParser()
            try:
                parser.parse(self._get(origin + "/robots.txt").decode("utf-8", "replace").splitlines())
            except FetchError as exc:
                if exc.kind != "not_found":
                    raise
                parser.parse([])
            self.robots[origin] = parser
        parser = self.robots[origin]
        if not parser.can_fetch(AGENT, url):
            raise FetchError("robots_disallowed")
        delay = parser.crawl_delay(AGENT) or parser.crawl_delay("*") or 1
        self.sleep(min(max(delay, 1), 60))
        return self._get(url)
