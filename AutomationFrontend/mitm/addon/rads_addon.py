"""mitmproxy addon — rads-tracker capture + local JSON API.

Run with:  mitmdump -s rads_addon.py --listen-port 8080

Captures:
  - All flows (rolling buffer, last MAX_FLOWS)
  - Special index of POST /api/rads-tracker/event with parsed JSON body

Exposes a plain HTTP API (no auth) on API_PORT:
  GET  /health                      → {"ok": true, "flows": N, "events": M}
  GET  /flows?limit=50              → recent flows (summary)
  GET  /events                      → all captured rads-tracker events
  GET  /events?type=render          → filter by event type
  GET  /events?placement=headline-data-zero
  GET  /events?adToken=ADS-...
  POST /reset                       → clear all buffers
  GET  /probe?host=example.com      → 1 if a successful TLS flow to <host>
                                      exists in recent flows, 0 otherwise
                                      (used by setup.py verify)
"""

from __future__ import annotations

import json
import threading
import time
from collections import deque
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import parse_qs, urlparse

from mitmproxy import http, ctx

API_PORT = 8082
MAX_FLOWS = 1000
RADS_PATH = "/api/rads-tracker/event"


# ─── shared state ───────────────────────────────────────────────────────────
class State:
    def __init__(self):
        self.lock = threading.Lock()
        self.flows: deque[dict] = deque(maxlen=MAX_FLOWS)
        self.events: list[dict] = []
        self.tls_failures: deque[dict] = deque(maxlen=200)

    def add_flow(self, summary: dict):
        with self.lock:
            self.flows.append(summary)

    def add_event(self, evt: dict):
        with self.lock:
            self.events.append(evt)

    def snapshot_flows(self, limit: int = 50) -> list[dict]:
        with self.lock:
            return list(self.flows)[-limit:]

    def snapshot_events(self) -> list[dict]:
        with self.lock:
            return list(self.events)

    def add_tls_failure(self, info: dict):
        with self.lock:
            self.tls_failures.append(info)

    def snapshot_tls(self) -> list[dict]:
        with self.lock:
            return list(self.tls_failures)

    def reset(self):
        with self.lock:
            self.flows.clear()
            self.events.clear()
            self.tls_failures.clear()


STATE = State()


# ─── HTTP API server (no auth, no XSRF) ─────────────────────────────────────
class APIHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        return  # silence

    def _json(self, status: int, body: Any):
        data = json.dumps(body).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):  # noqa: N802
        u = urlparse(self.path)
        q = parse_qs(u.query)

        if u.path == "/health":
            return self._json(200, {
                "ok": True,
                "flows": len(STATE.flows),
                "events": len(STATE.events),
                "tls_failures": len(STATE.tls_failures),
            })

        if u.path == "/tls_failures":
            return self._json(200, STATE.snapshot_tls())

        if u.path == "/flows":
            limit = int(q.get("limit", ["50"])[0])
            return self._json(200, STATE.snapshot_flows(limit))

        if u.path == "/events":
            events = STATE.snapshot_events()
            for k in ("type", "placement", "adToken", "source", "productId"):
                if k in q:
                    val = q[k][0]
                    events = [e for e in events if e.get(k) == val]
            return self._json(200, events)

        if u.path == "/probe":
            host = q.get("host", [""])[0]
            if not host:
                return self._json(400, {"error": "host required"})
            for f in STATE.snapshot_flows(200):
                if host in f.get("host", "") and f.get("status_code", 0) > 0:
                    return self._json(200, {"intercepted": True, "flow": f})
            return self._json(200, {"intercepted": False})

        return self._json(404, {"error": "not found"})

    def do_POST(self):  # noqa: N802
        u = urlparse(self.path)
        if u.path == "/reset":
            STATE.reset()
            return self._json(200, {"ok": True})
        return self._json(404, {"error": "not found"})


def _start_api():
    srv = ThreadingHTTPServer(("127.0.0.1", API_PORT), APIHandler)
    t = threading.Thread(target=srv.serve_forever, name="rads-api", daemon=True)
    t.start()
    return srv


# ─── mitmproxy hooks ────────────────────────────────────────────────────────
class RadsAddon:
    def __init__(self):
        self._srv = None

    def running(self):
        if self._srv is None:
            self._srv = _start_api()
            ctx.log.info(f"[rads-addon] API listening on http://127.0.0.1:{API_PORT}")

    def response(self, flow: http.HTTPFlow):
        req = flow.request
        resp = flow.response

        summary = {
            "ts": time.time(),
            "method": req.method,
            "scheme": req.scheme,
            "host": req.pretty_host,
            "port": req.port,
            "path": req.path,
            "status_code": resp.status_code if resp else 0,
            "content_type": resp.headers.get("content-type", "") if resp else "",
        }
        STATE.add_flow(summary)

        if RADS_PATH not in req.path or req.method != "POST":
            return

        try:
            body = req.get_text() or ""
            payload = json.loads(body)
        except Exception as e:
            ctx.log.warn(f"[rads-addon] could not parse body: {e}")
            return

        # Extract a row per item, so each adToken becomes its own event row.
        evt_type = payload.get("type")
        data = payload.get("data") or {}
        user_data = data.get("userData") or {}
        items = data.get("items") or []
        if not items:
            items = [{}]

        for idx, item in enumerate(items):
            # Rappi envía 'properties' (lowercase) pero algunas variantes pueden traer 'Properties' — soportamos ambas.
            props = item.get("properties") or item.get("Properties") or {}
            event_row = {
                "ts": time.time(),
                "type": evt_type,
                "adToken": item.get("adToken"),
                "placement": props.get("placement") or props.get("placementId"),
                "source": props.get("source") or user_data.get("source"),
                "campaignId": props.get("campaignId") or props.get("campaign_id"),
                "productId": props.get("productId") or props.get("product_id") or props.get("id"),
                "price": props.get("price"),
                "index": props.get("index"),
                "itemIndex": idx,
                "host": req.pretty_host,
                "raw": payload,
            }
            STATE.add_event(event_row)
            ctx.log.info(
                f"[rads-addon] {evt_type:>18}  "
                f"adToken={event_row['adToken']}  "
                f"placement={event_row['placement']}  "
                f"source={event_row['source']}"
            )

    def tls_failed_client(self, data):
        """Catch TLS handshake failures (cert not trusted by device)."""
        try:
            sni = getattr(data, "client_conn", None) and data.client_conn.sni
        except Exception:
            sni = None
        try:
            conn = getattr(data, "conn", None) or getattr(data, "client_conn", None)
            error = ""
            if conn is not None:
                error = getattr(conn, "error", "") or ""
        except Exception:
            error = ""
        info = {
            "ts": time.time(),
            "sni": sni or "",
            "error": str(error),
        }
        STATE.add_tls_failure(info)
        ctx.log.info(f"[rads-addon] TLS failure sni={info['sni']} err={info['error']}")

    def error(self, flow: http.HTTPFlow):
        # Capture TLS / connect errors too — useful for the probe.
        try:
            req = flow.request
            STATE.add_flow({
                "ts": time.time(),
                "method": req.method if req else "",
                "host": (req.pretty_host if req else "") or "",
                "path": (req.path if req else "") or "",
                "status_code": 0,
                "error": str(flow.error) if flow.error else "unknown",
            })
        except Exception:
            pass


addons = [RadsAddon()]
