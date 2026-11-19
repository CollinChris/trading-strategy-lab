"""SEC EDGAR access for the insider and earnings studies.

SEC's fair-access policy requires a User-Agent naming the requester with a contact
email (requests without one get HTTP 403) and at most 10 requests a second. The
contact comes from the SEC_USER_AGENT environment variable (a repository secret on
GitHub Actions) — it is never hard-coded here.
"""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path

SEC_DIR = Path("data/research/sec")
TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"
SUBMISSIONS_URL = "https://data.sec.gov/submissions/{name}"
FORM345_URL = (
    "https://www.sec.gov/files/structureddata/data/insider-transactions-data-sets/"
    "{year}q{quarter}_form345.zip"
)
MIN_INTERVAL = 0.125  # 8 requests/second, under SEC's limit of 10


def user_agent() -> str:
    ua = os.environ.get("SEC_USER_AGENT", "").strip()
    if "@" not in ua:
        raise SystemExit(
            "SEC_USER_AGENT must be set to 'Your Name your.email@example.com' — SEC rejects "
            "requests without a contact (https://www.sec.gov/os/accessing-edgar-data). "
            "On GitHub: gh secret set SEC_USER_AGENT"
        )
    return ua


class SecClient:
    def __init__(self, ua: str | None = None):
        self.headers = {"User-Agent": ua or user_agent()}
        self._last = 0.0

    def get(self, url: str, tries: int = 5) -> bytes | None:
        """Body bytes, or None for 404 (e.g. a quarter not yet published)."""
        for attempt in range(tries):
            wait = self._last + MIN_INTERVAL - time.monotonic()
            if wait > 0:
                time.sleep(wait)
            self._last = time.monotonic()
            try:
                req = urllib.request.Request(url, headers=self.headers)
                with urllib.request.urlopen(req, timeout=120) as resp:
                    return resp.read()
            except urllib.error.HTTPError as exc:
                if exc.code == 404:
                    return None
                if exc.code == 403:
                    raise SystemExit(
                        f"SEC refused {url} (403) — check SEC_USER_AGENT has a real contact "
                        "email, and that the 10 requests/second limit isn't being exceeded."
                    ) from exc
                if exc.code not in (429, 500, 502, 503, 504) or attempt == tries - 1:
                    raise
            except (urllib.error.URLError, TimeoutError, ConnectionError):
                if attempt == tries - 1:
                    raise
            time.sleep(min(60, 5 * 2**attempt))
        raise RuntimeError("unreachable")

    def get_json(self, url: str) -> dict | None:
        body = self.get(url)
        return None if body is None else json.loads(body)

    def cached(self, url: str, path: Path) -> Path | None:
        """Download once to `path`; None if the file doesn't exist upstream."""
        if path.exists():
            return path
        body = self.get(url)
        if body is None:
            return None
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(path.suffix + ".part")
        tmp.write_bytes(body)
        tmp.replace(path)
        return path


def ticker_map(client: SecClient) -> dict[int, list[str]]:
    """CIK → its current tickers in SEC's order (primary listing first)."""
    data = client.get_json(TICKERS_URL) or {}
    out: dict[int, list[str]] = {}
    for row in data.values():
        out.setdefault(int(row["cik_str"]), []).append(str(row["ticker"]).upper())
    return out


def to_alpaca(ticker: str) -> str:
    """SEC writes share classes with a dash (BRK-B); Alpaca with a dot (BRK.B)."""
    return ticker.strip().upper().replace("-", ".")
