#!/usr/bin/env python3
"""mitm/setup.py — cross-platform mitmproxy setup for Rappi rads-tracker capture.

Subcommands:
  info             Show host IP, port, OS, mitmproxy status
  start            Start mitmweb in background
  stop             Stop mitmweb
  device           Detect Android (via adb) or guide iOS user; install CA cert, set proxy
  disable-device   Clear all proxy settings from Android device via adb
  test             Verify device traffic flows through mitmproxy
"""

import argparse
import json
import os
import platform
import shutil
import signal
import socket
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

PROXY_PORT = 8080
API_PORT = 8082
MITM_DIR = Path.home() / ".mitmproxy"
PID_FILE = MITM_DIR / "mitm-setup.pid"
LOG_FILE = MITM_DIR / "mitmdump.log"
CERT_PEM = MITM_DIR / "mitmproxy-ca-cert.pem"
ADDON = Path(__file__).resolve().parent / "addon" / "rads_addon.py"


class C:
    OK = "\033[92m"
    WARN = "\033[93m"
    ERR = "\033[91m"
    INFO = "\033[96m"
    BOLD = "\033[1m"
    END = "\033[0m"


def _supports_color():
    return sys.stdout.isatty() and platform.system() != "Windows" or os.environ.get("TERM")


if not _supports_color():
    for attr in ("OK", "WARN", "ERR", "INFO", "BOLD", "END"):
        setattr(C, attr, "")


def ok(msg):     print(f"{C.OK}OK{C.END}   {msg}")
def warn(msg):   print(f"{C.WARN}WARN{C.END} {msg}")
def err(msg):    print(f"{C.ERR}FAIL{C.END} {msg}")
def info(msg):   print(f"{C.INFO}INFO{C.END} {msg}")
def header(msg): print(f"\n{C.BOLD}── {msg} ──{C.END}")


# ─── helpers ────────────────────────────────────────────────────────────────
def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"
    finally:
        s.close()


def host_os():
    return platform.system()  # 'Darwin' | 'Windows' | 'Linux'


def mitmproxy_installed():
    return shutil.which("mitmdump") is not None and shutil.which("mitmweb") is not None


def _port_open(port, host="127.0.0.1", timeout=1.0):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        s.connect((host, port))
        return True
    except Exception:
        return False
    finally:
        s.close()


def mitmweb_running():
    """Proxy port + addon API port both listening = mitmdump+addon is up."""
    return _port_open(PROXY_PORT) and _port_open(API_PORT)


def _api_get(path):
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{API_PORT}{path}", timeout=3) as r:
            return json.load(r)
    except Exception:
        return None


def _api_post(path, body=b""):
    try:
        req = urllib.request.Request(
            f"http://127.0.0.1:{API_PORT}{path}", data=body, method="POST"
        )
        with urllib.request.urlopen(req, timeout=3) as r:
            return json.load(r)
    except Exception:
        return None


def mitmweb_flow_count():
    h = _api_get("/health")
    return h.get("flows", 0) if h else 0


def mitmweb_event_count():
    h = _api_get("/health")
    return h.get("events", 0) if h else 0


def mitmweb_recent_flows(n=50):
    data = _api_get(f"/flows?limit={n}")
    return data if isinstance(data, list) else []


def api_probe(host):
    return _api_get(f"/probe?host={host}") or {}


def adb_available():
    return shutil.which("adb") is not None


def adb_devices():
    if not adb_available():
        return []
    try:
        out = subprocess.check_output(["adb", "devices"], text=True, timeout=5)
        return [
            l.split()[0]
            for l in out.strip().splitlines()[1:]
            if l.strip() and l.endswith("device")
        ]
    except Exception:
        return []


def adb_shell(serial, *args, timeout=20):
    return subprocess.run(
        ["adb", "-s", serial, "shell", *args],
        capture_output=True, text=True, timeout=timeout,
    )


def detect_ios_mac():
    """Best-effort iOS device detection on macOS (returns name or None)."""
    if host_os() != "Darwin":
        return None
    try:
        out = subprocess.check_output(
            ["system_profiler", "SPUSBDataType"], text=True, timeout=5
        )
        for line in out.splitlines():
            ll = line.strip().lower()
            if "iphone" in ll or "ipad" in ll:
                return line.strip()
    except Exception:
        pass
    return None


# ─── commands ───────────────────────────────────────────────────────────────
def cmd_info(_):
    header("Host info")
    ip = get_local_ip()
    print(f"  OS:           {host_os()}")
    print(f"  Local IP:     {C.BOLD}{ip}{C.END}")
    print(f"  Proxy port:   {C.BOLD}{PROXY_PORT}{C.END}")
    print(f"  Addon API:    http://127.0.0.1:{API_PORT}  (events JSON)")
    print()
    print(f"  → On your device set Wi-Fi proxy to:")
    print(f"        Host: {C.BOLD}{ip}{C.END}")
    print(f"        Port: {C.BOLD}{PROXY_PORT}{C.END}")

    header("mitmproxy")
    if not mitmproxy_installed():
        err("mitmproxy not installed")
        if host_os() == "Darwin":
            print("    Install: brew install mitmproxy")
        elif host_os() == "Windows":
            print("    Install: choco install mitmproxy  (or download from https://mitmproxy.org)")
        else:
            print("    Install: pip install mitmproxy")
        return 1
    ok("mitmproxy CLI installed")

    if mitmweb_running():
        ok(f"mitmweb is running ({mitmweb_flow_count()} flows captured)")
    else:
        warn(f"mitmweb not running — start it with: setup.py start")

    if CERT_PEM.exists():
        ok(f"CA cert present at {CERT_PEM}")
    else:
        warn("CA cert not generated yet — start mitmweb once to generate it")

    header("Device tooling")
    if adb_available():
        devices = adb_devices()
        if devices:
            ok(f"adb sees {len(devices)} Android device(s): {', '.join(devices)}")
        else:
            warn("adb installed but no Android device connected/authorized")
    else:
        warn("adb not in PATH (only needed for Android automation)")

    ios = detect_ios_mac()
    if ios:
        info(f"iOS device detected via USB: {ios}")

    return 0


def cmd_start(_):
    if not mitmproxy_installed():
        err("mitmproxy not installed — run `setup.py info` for install steps")
        return 1
    if mitmweb_running():
        ok("mitmdump+addon already running")
        return 0
    if not ADDON.exists():
        err(f"addon not found at {ADDON}")
        return 1

    MITM_DIR.mkdir(parents=True, exist_ok=True)
    cmd = ["mitmdump",
           "-s", str(ADDON),
           "--listen-port", str(PROXY_PORT),
           "--set", "console_eventlog_verbosity=info"]
    info(f"Launching: {' '.join(cmd)}")

    log = open(LOG_FILE, "w")
    if host_os() == "Windows":
        DETACHED = 0x00000008
        p = subprocess.Popen(cmd, stdout=log, stderr=subprocess.STDOUT,
                             creationflags=DETACHED)
    else:
        p = subprocess.Popen(cmd, stdout=log, stderr=subprocess.STDOUT,
                             start_new_session=True)
    PID_FILE.write_text(str(p.pid))

    # wait up to 8s for both ports to come up
    for _ in range(16):
        time.sleep(0.5)
        if mitmweb_running():
            ok(f"mitmdump started (pid {p.pid})")
            print(f"     Proxy:    {get_local_ip()}:{PROXY_PORT}")
            print(f"     API:      http://127.0.0.1:{API_PORT}")
            print(f"     Log:      {LOG_FILE}")
            return 0

    err(f"mitmdump did not respond — check {LOG_FILE}")
    return 1


def cmd_stop(_):
    if not PID_FILE.exists():
        warn("No PID file (mitmweb wasn't started by this script)")
        return 0
    try:
        pid = int(PID_FILE.read_text())
        if host_os() == "Windows":
            subprocess.run(["taskkill", "/F", "/PID", str(pid)],
                           check=False, capture_output=True)
        else:
            os.kill(pid, signal.SIGTERM)
        ok(f"Stopped mitmweb (pid {pid})")
    except ProcessLookupError:
        warn("Process already stopped")
    except Exception as e:
        err(f"Could not stop process: {e}")
    PID_FILE.unlink(missing_ok=True)
    return 0


def cmd_device(_):
    if not CERT_PEM.exists():
        err(f"CA cert not found at {CERT_PEM}")
        info("Start mitmweb at least once: setup.py start")
        return 1
    if not mitmweb_running():
        warn("mitmweb is not running. Some checks will be skipped.")
        info("To enable connectivity test, start mitmweb first: setup.py start")

    ip = get_local_ip()
    devices = adb_devices()

    if devices:
        if len(devices) > 1:
            info(f"Multiple Android devices detected: {devices} — using {devices[0]}")
        return setup_android(devices[0], ip)

    ios = detect_ios_mac()
    if ios:
        header(f"iOS device detected ({ios})")
        info("Full automation is not possible for iOS. Follow guided steps below.")
        return setup_manual(ip, focus="ios")

    header("No device auto-detected")
    info("If you have Android with USB debugging on, plug it in and authorize adb.")
    return setup_manual(ip, focus="both")


def setup_android(serial, ip):
    header(f"Android device: {serial}")
    expected_proxy = f"{ip}:{PROXY_PORT}"

    # 1. Proxy
    r = adb_shell(serial, "settings", "get", "global", "http_proxy")
    current = r.stdout.strip()
    if current == expected_proxy:
        ok(f"Proxy already set to {expected_proxy}")
    else:
        info(f"Setting proxy: {current or '(none)'} → {expected_proxy}")
        adb_shell(serial, "settings", "put", "global", "http_proxy", expected_proxy)
        ok(f"Proxy set to {expected_proxy}")

    # 2. Check cert via TLS probe (Chrome intent)
    if mitmweb_running():
        header("Checking if CA cert is already trusted")
        if probe_tls_android(serial):
            ok("CA cert is trusted by the device — setup complete")
            print()
            info(f"To clear the proxy later: adb -s {serial} shell settings put global http_proxy :0")
            return 0
        warn("CA cert is NOT trusted yet — installing")
    else:
        warn("Skipping trust check (mitmweb not running). Proceeding to install cert anyway.")

    # 3. Install cert
    return install_android_cert(serial)


def probe_tls_android(serial, url="https://example.com", wait_sec=6):
    """Open URL on device via Chrome intent, watch mitmweb for a successful TLS flow."""
    before = mitmweb_flow_count()
    info(f"Opening {url} on device to test TLS interception...")
    adb_shell(serial, "am", "start", "-a", "android.intent.action.VIEW", "-d", url)
    time.sleep(wait_sec)
    flows = mitmweb_recent_flows(50)
    host_part = url.split("//", 1)[1].split("/", 1)[0]
    for f in flows:
        req = f.get("request", {})
        if host_part in (req.get("pretty_host") or req.get("host") or ""):
            resp = f.get("response")
            if resp and resp.get("status_code", 0) > 0:
                info(f"Captured flow to {host_part} with status {resp['status_code']} → cert trusted")
                return True
    return False


def install_android_cert(serial):
    target = "/sdcard/Download/mitmproxy-ca-cert.crt"
    info(f"Pushing CA cert → device:{target}")
    r = subprocess.run(["adb", "-s", serial, "push", str(CERT_PEM), target],
                       capture_output=True, text=True)
    if r.returncode != 0:
        err(f"adb push failed: {r.stderr.strip()}")
        return 1
    ok("Cert pushed to device Downloads folder")

    info("Opening Settings → Security on the device")
    adb_shell(serial, "am", "start", "-a", "android.settings.SECURITY_SETTINGS")

    print()
    print(f"{C.BOLD}Steps on the device:{C.END}")
    print("  1. Settings → Security → Encryption & credentials")
    print("     (some OEMs: Settings → Security → More security settings)")
    print("  2. Tap 'Install a certificate' → 'CA certificate'")
    print("  3. Tap 'Install anyway' on the warning")
    print("  4. Choose mitmproxy-ca-cert.crt from Downloads")
    print("  5. Give it any name (e.g. 'mitmproxy')")
    print()
    try:
        input(f"{C.BOLD}Press ENTER when the cert is installed...{C.END}")
    except KeyboardInterrupt:
        print()
        return 1

    if not mitmweb_running():
        warn("mitmweb is not running — can't verify trust automatically")
        info("Start mitmweb and run: setup.py test")
        return 0

    header("Re-checking trust")
    if probe_tls_android(serial):
        ok("CA cert installed and trusted!")
        print()
        warn("Android 7+ apps only trust user CAs if their network_security_config allows it.")
        warn("If Rappi traffic doesn't appear, you need the QA/debug APK that trusts user CAs.")
        return 0

    err("Cert still not trusted. Verify: Settings → Security → Trusted credentials → User tab")
    return 1


def setup_manual(ip, focus="both"):
    print()
    print(f"{C.BOLD}1) Connect device to the SAME Wi-Fi as this computer{C.END}")
    print()
    print(f"{C.BOLD}2) Set HTTP proxy on the device{C.END}")
    print(f"        Host: {C.BOLD}{ip}{C.END}")
    print(f"        Port: {C.BOLD}{PROXY_PORT}{C.END}")
    print()
    if focus in ("android", "both"):
        print(f"   {C.BOLD}Android:{C.END} Wi-Fi → long-press the network → Modify → Advanced → Proxy: Manual")
    if focus in ("ios", "both"):
        print(f"   {C.BOLD}iOS:{C.END}     Settings → Wi-Fi → (i) on the network → Configure Proxy → Manual")
    print()
    print(f"{C.BOLD}3) Install the mitmproxy CA cert{C.END}")
    print(f"   Open browser on device → http://mitm.it → tap your OS")
    print()
    if focus in ("android", "both"):
        print(f"   {C.BOLD}Android:{C.END}")
        print(f"      Settings → Security → Encryption & credentials → Install a certificate → CA certificate")
        print(f"      Pick the downloaded .crt and confirm.")
    if focus in ("ios", "both"):
        print(f"   {C.BOLD}iOS:{C.END}")
        print(f"      Allow profile download → Settings → General → VPN & Device Management → install profile")
        print(f"      Then Settings → General → About → Certificate Trust Settings → enable 'mitmproxy'")
    print()
    print(f"{C.BOLD}4) Verify everything works{C.END}")
    print(f"   Run: {C.BOLD}python3 {Path(sys.argv[0]).name} test{C.END}")
    print()
    return 0


def cmd_test(_):
    header("Connection test")
    if not mitmweb_running():
        err("mitmweb is not running — start it first: setup.py start")
        return 1

    before = mitmweb_flow_count()
    info(f"Currently captured flows: {before}")
    print()
    print(f"{C.BOLD}On your device, open any HTTPS site (e.g. https://example.com) or the Rappi app.{C.END}")
    print("Watching for new flows for 30 seconds...")
    print()

    deadline = time.time() + 30
    last = before
    while time.time() < deadline:
        time.sleep(2)
        now = mitmweb_flow_count()
        if now > last:
            print(f"  +{now - last} new flow(s) (total: {now})")
            last = now

    print()
    if last == before:
        err("No flows captured. Check:")
        print("  - Device and computer on the same Wi-Fi")
        print(f"  - Device proxy set to {get_local_ip()}:{PROXY_PORT}")
        print("  - CA cert installed AND trusted on device")
        return 1

    ok(f"Captured {last - before} new flow(s) — proxy connection works")

    # Look for rads-tracker specifically
    rads = []
    for f in mitmweb_recent_flows(100):
        req = f.get("request", {})
        path = req.get("path") or ""
        if "rads-tracker" in path:
            rads.append(f)

    if rads:
        ok(f"Found {len(rads)} rads-tracker event(s) — ready to validate Ads events")
        for f in rads[-5:]:
            req = f.get("request", {})
            host = req.get("pretty_host", req.get("host", "?"))
            print(f"     POST https://{host}{req.get('path', '')}")
    else:
        warn("No rads-tracker events yet — open Rappi and trigger an Ads-related flow to capture them")

    return 0


def cmd_verify(_):
    """Automated TLS verification: open https://example.com on device, check capture."""
    header("Automated verification — does mitmproxy intercept TLS from the device?")
    if not mitmweb_running():
        err("mitmproxy/addon not running — start with: setup.py start")
        return 1

    devices = adb_devices()
    if not devices:
        err("No Android device via adb. Plug device with USB debugging enabled, or use `setup.py test` to verify manually.")
        return 1
    serial = devices[0]

    # Check Wi-Fi proxy on device
    info(f"Device: {serial}")
    dump = subprocess.run(["adb", "-s", serial, "shell", "dumpsys", "wifi"],
                          capture_output=True, text=True, timeout=10)
    proxy_line = ""
    for line in dump.stdout.splitlines():
        if "HttpProxy:" in line and "8080" in line:
            proxy_line = line.strip()
            break
    if proxy_line:
        ok(f"Device Wi-Fi proxy line: {proxy_line}")
    else:
        warn("Could not confirm Wi-Fi proxy on device via dumpsys. Make sure it points to "
             f"{get_local_ip()}:{PROXY_PORT}.")

    # Reset addon buffers so the probe is clean
    _api_post("/reset")
    info("Buffers cleared. Waking device and triggering fresh HTTPS request...")

    adb_shell(serial, "input", "keyevent", "KEYCODE_WAKEUP")
    time.sleep(1)
    # Cache-busting URL forces a fresh network request
    probe_url = f"https://example.com/?probe={int(time.time())}"
    adb_shell(serial, "am", "start", "-a", "android.intent.action.VIEW", "-d", probe_url)

    # Poll up to 30s for either a successful flow OR a TLS failure
    deadline = time.time() + 30
    result = None
    while time.time() < deadline:
        time.sleep(1)
        r = api_probe("example.com")
        if r.get("intercepted"):
            result = r
            break
        tls = _api_get("/tls_failures") or []
        rel = [t for t in tls if "example.com" in (t.get("sni") or "")]
        # also flag general TLS failures (any host) — proves cert untrusted system-wide
        if rel or tls:
            result = {"intercepted": False, "tls_failures": rel or tls}
            break

    print()
    header("Result")
    if result and result.get("intercepted"):
        flow = result.get("flow", {})
        ok(f"TLS intercepted successfully: {flow.get('method')} https://{flow.get('host')}{flow.get('path')} → {flow.get('status_code')}")
        ok("CA cert is trusted by the device. Proxy + cert are working.")
        return 0

    if result and result.get("tls_failures"):
        err("CA cert is NOT trusted by the device (TLS handshake rejected by client).")
        for t in result["tls_failures"][:5]:
            print(f"     sni={t.get('sni','?')}  err={t.get('error','?')}")
        info("Fix: run `setup.py device` to push the cert and install it,")
        info("     or manually open http://mitm.it on the device and install the Android cert.")
        return 1

    err("No flows to example.com captured. Check that the device proxy is really pointing here.")
    info(f"Device should have proxy = {get_local_ip()}:{PROXY_PORT}")
    return 1


def cmd_reset(_):
    if not mitmweb_running():
        err("mitmproxy/addon not running")
        return 1
    r = _api_post("/reset")
    if r and r.get("ok"):
        ok("Addon buffers cleared")
        return 0
    err("Reset failed")
    return 1


def _clear_android_proxy(serial):
    header(f"Android device: {serial}")
    targets = [
        ("global", "http_proxy"),
        ("global", "http_proxy_host"),
        ("global", "http_proxy_port"),
        ("global", "http_proxy_exclusion_list"),
    ]
    for ns, key in targets:
        r = adb_shell(serial, "settings", "get", ns, key)
        current = r.stdout.strip()
        if current and current not in ("null", ":0"):
            adb_shell(serial, "settings", "delete", ns, key)
            ok(f"Cleared {key} (was: {current})")
        else:
            info(f"Skipped {key} (not set)")
    adb_shell(serial, "settings", "put", "global", "http_proxy", ":0")
    ok("http_proxy set to :0 (disabled)")
    header("Verification")
    for ns, key in targets:
        r = adb_shell(serial, "settings", "get", ns, key)
        val = r.stdout.strip()
        if val in ("", "null", ":0"):
            ok(f"{key}: cleared")
        else:
            warn(f"{key}: still set to '{val}'")
    return 0


def cmd_disable_device(_):
    if not adb_available():
        err("adb not found in PATH — install Android SDK Platform-Tools")
        return 1
    devices = adb_devices()
    if not devices:
        err("No Android device connected via adb")
        info("Connect device via USB with USB debugging enabled and authorized")
        return 1
    if len(devices) > 1:
        info(f"Multiple devices detected: {devices} — using {devices[0]}")
    return _clear_android_proxy(devices[0])


# ─── main ───────────────────────────────────────────────────────────────────
def main():
    p = argparse.ArgumentParser(
        description="Cross-platform mitmproxy setup for Rappi rads-tracker capture"
    )
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("info",           help="Show host IP, port, OS, mitmproxy status")
    sub.add_parser("start",          help="Start mitmdump + rads_addon in background")
    sub.add_parser("stop",           help="Stop mitmdump")
    sub.add_parser("device",         help="Configure device proxy and install CA cert")
    sub.add_parser("disable-device", help="Clear all proxy settings from Android device")
    sub.add_parser("test",           help="Interactive: open Rappi on device and watch for flows")
    sub.add_parser("verify",         help="Automated TLS probe via adb (example.com)")
    sub.add_parser("reset",          help="Clear addon buffers (flows + events)")
    args = p.parse_args()

    fn = {
        "info":           cmd_info,
        "start":          cmd_start,
        "stop":           cmd_stop,
        "device":         cmd_device,
        "disable-device": cmd_disable_device,
        "test":           cmd_test,
        "verify":         cmd_verify,
        "reset":          cmd_reset,
    }[args.cmd]
    sys.exit(fn(args) or 0)


if __name__ == "__main__":
    main()
