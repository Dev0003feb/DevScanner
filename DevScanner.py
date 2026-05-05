#!/usr/bin/env python3
# ================================================================
#   —͟͞⛦⃕͜᪾ 𝐃𝐄𝐕࿐  &  T-REX  —  ULTRA SCANNER  v3.1
#   Professional · Optimized · All-Device Compatible
# ================================================================

import socket, ssl, sys, os, json, time, threading, re, subprocess
import ipaddress
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

# ── ANSI COLORS (Premium Hacker Theme) ──────────────────────────
R   = "\033[38;5;196m"    # Crimson Red (Bright)
G   = "\033[38;5;46m"     # Neon Green
Y   = "\033[38;5;226m"    # Vibrant Yellow
B   = "\033[38;5;33m"     # Electric Blue
M   = "\033[38;5;38m"     # Deep Sky Blue (Purple replaced)
C   = "\033[38;5;51m"     # Bright Aqua/Cyan
W   = "\033[38;5;255m"    # Pure White
O   = "\033[38;5;208m"    # Neon Orange
LB  = "\033[38;5;117m"    # Light Sky Blue
PU  = "\033[38;5;82m"     # Toxic/Mint Green (Purple replaced)
CY2 = "\033[38;5;87m"     # Light Cyan
GR2 = "\033[38;5;118m"    # Chartreuse (Yellow-Green)
DIM = "\033[2m"           # Dim text
BLD = "\033[1m"           # Bold text
RST = "\033[0m"           # Reset all formatting
CL  = "\033[2K"           # Clear Line
CR  = "\r"                # Carriage Return


# ── GitHub raw URL for update ────────────────────────────────────
TOOL_URL = "https://raw.githubusercontent.com/Dev0003feb/DevScanner/main/DevScanner.py"
TOOL_VER = "v4.0"

# ================================================================
#  DEVICE DETECTION
# ================================================================
def detect_device():
    try:
        import multiprocessing
        cores = multiprocessing.cpu_count()
    except:
        cores = 1
    ram_mb = 512
    try:
        with open("/proc/meminfo") as f:
            for line in f:
                if "MemTotal" in line:
                    ram_mb = int(line.split()[1]) // 1024
                    break
    except:
        pass
    if cores <= 2 or ram_mb < 1500:
        return "LOW",  10, 2.0
    elif cores <= 4 or ram_mb < 3500:
        return "MID",  30, 1.2
    else:
        return "HIGH", 50, 0.7

TIER, DEFAULT_THREADS, TIMEOUT = detect_device()

# ================================================================
#  HELPERS
# ================================================================
def clr():
    os.system("clear")

def is_online():
    targets = [
        ("8.8.8.8",53),("1.1.1.1",53),("8.8.4.4",53),
        ("8.8.8.8",80),("1.1.1.1",80),("208.67.222.222",53),
    ]
    for host, port in targets:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(2)
            s.connect((host, port))
            s.close()
            return True
        except:
            continue
    return False

def safe_path(p):
    return os.path.expanduser(p.strip().strip("'\""))

# ================================================================
#  FILE BROWSER  ── Interactive storage navigator
# ================================================================
# Android common storage roots
STORAGE_ROOTS = [
    "/storage/emulated/0",
    "/sdcard",
    os.path.expanduser("~/storage/shared"),
    os.path.expanduser("~/storage/downloads"),
    os.path.expanduser("~"),
]

def file_browser(only_ext=".txt"):
    """
    Interactive file browser.
    Returns selected file path or None if cancelled.
    Commands:
      [number]  → enter folder OR select file
      ..        → go up one level
      /         → go to storage root menu
      q         → cancel / go back to manual input
    """
    # Find a valid starting directory
    start = None
    for r in STORAGE_ROOTS:
        if os.path.isdir(r):
            start = r
            break
    if not start:
        start = os.path.expanduser("~")

    current = start

    while True:
        clr()
        # ── Header ──────────────────────────────────────────────
        print(f"\n{M}╔══════════════════════════════════════════════════╗{RST}")
        print(f"{M}║{RST}  {BLD}{C}📂  FILE BROWSER{RST}                              {M}║{RST}")
        print(f"{M}╠══════════════════════════════════════════════════╣{RST}")

        # Current path — wrap if too long
        disp = current if len(current) <= 44 else "…" + current[-43:]
        pad  = 48 - len(disp)
        print(f"{M}║{RST}  {Y}{disp}{RST}{' '*max(0,pad)}{M}║{RST}")
        print(f"{M}╠══════════════════════════════════════════════════╣{RST}")

        # ── List directory contents ──────────────────────────────
        try:
            entries_raw = os.listdir(current)
        except PermissionError:
            print(f"{M}║{RST}  {R}Permission denied{RST}                             {M}║{RST}")
            print(f"{M}╚══════════════════════════════════════════════════╝{RST}")
            input(f"\n  {W}Enter dabao...{RST}")
            # Go up
            current = os.path.dirname(current)
            continue

        # Separate folders and matching files
        folders = sorted([e for e in entries_raw
                          if os.path.isdir(os.path.join(current, e))
                          and not e.startswith(".")],
                         key=str.lower)
        files   = sorted([e for e in entries_raw
                          if os.path.isfile(os.path.join(current, e))
                          and (only_ext == "*" or e.lower().endswith(only_ext))],
                         key=str.lower)

        entries = []  # combined list: (type, name)
        for f in folders: entries.append(("D", f))
        for f in files:   entries.append(("F", f))

        # Print entries with numbers
        if not entries:
            print(f"{M}║{RST}  {DIM}(Koi .txt file ya folder nahi mila){RST}           {M}║{RST}")
        else:
            for i, (typ, name) in enumerate(entries, 1):
                icon = f"{C}📁{RST}" if typ == "D" else f"{G}📄{RST}"
                # Truncate long names
                dname = (name[:38] + "…") if len(name) > 39 else name
                num   = f"{Y}{i:<3}{RST}"
                row   = f"  {num} {icon} {dname}"
                vis   = 6 + len(dname) + 1
                pad2  = max(0, 48 - vis)
                print(f"{M}║{RST}{row}{' '*pad2}{M}║{RST}")

        print(f"{M}╠══════════════════════════════════════════════════╣{RST}")
        print(f"{M}║{RST}  {DIM}[number] Open  │ [..] Back  │ [/] Root  │ [q] Cancel{RST}  {M}║{RST}")
        print(f"{M}╚══════════════════════════════════════════════════╝{RST}")

        cmd = input(f"\n  {W}◈  : {RST}").strip()

        # ── Commands ────────────────────────────────────────────
        if cmd.lower() == "q":
            return None  # cancelled → go back to manual input

        elif cmd == "..":
            parent = os.path.dirname(current)
            if parent != current:
                current = parent

        elif cmd == "/":
            # Show storage roots to choose from
            clr()
            print(f"\n{M}╔══════════════════════════════════════════════════╗{RST}")
            print(f"{M}║{RST}  {BLD}{C}Storage Roots{RST}                                 {M}║{RST}")
            print(f"{M}╠══════════════════════════════════════════════════╣{RST}")
            valid_roots = [(i+1, r) for i, r in enumerate(STORAGE_ROOTS) if os.path.isdir(r)]
            for num, r in valid_roots:
                rpad = max(0, 46 - len(r))
                print(f"{M}║{RST}  {Y}{num}{RST}  {r}{' '*rpad}{M}║{RST}")
            print(f"{M}╚══════════════════════════════════════════════════╝{RST}")
            rc = input(f"\n  {W}◈  Root number: {RST}").strip()
            try:
                ri = int(rc) - 1
                if 0 <= ri < len(valid_roots):
                    current = valid_roots[ri][1]
            except:
                pass

        elif cmd.isdigit():
            idx = int(cmd) - 1
            if 0 <= idx < len(entries):
                typ, name = entries[idx]
                full_path = os.path.join(current, name)
                if typ == "D":
                    current = full_path
                else:
                    # File selected!
                    clr()
                    print(f"\n  {G}✔  File selected:{RST}")
                    print(f"  {W}  {full_path}{RST}\n")
                    return full_path
            else:
                pass  # invalid number, just redraw
        else:
            pass  # unknown command, redraw


def ask_file_path(label="File", ext=".txt"):
    """
    Show 2 options:
    1. Type path manually
    2. Browse storage
    Returns the selected path or None
    """
    print(f"\n{M}  ┌────────────────────────────────────────┐{RST}")
    print(f"{M}  │{RST}  {BLD}{W}File Select karo{RST}                       {M}│{RST}")
    print(f"{M}  ├────────────────────────────────────────┤{RST}")
    print(f"{M}  │{RST}  {G}[1]{RST} {W}File path manually type karo{RST}       {M}│{RST}")
    print(f"{M}  │{RST}  {G}[2]{RST} {C}Storage browse karke file chuno{RST}    {M}│{RST}")
    print(f"{M}  │{RST}  {DIM}Enter = path manually type karo{RST}        {M}│{RST}")
    print(f"{M}  └────────────────────────────────────────┘{RST}")

    ch = input(f"\n  {W}◈  Choice: {RST}").strip()

    if ch == "2":
        result = file_browser(only_ext=ext)
        if result:
            return result
        else:
            # User cancelled browser → fall through to manual
            print(f"\n  {Y}Browser cancel — ab manually path daalo:{RST}")
            print(f"  {DIM}  e.g: /storage/emulated/0/Download/file.txt{RST}\n")
            raw = input(f"  {W}◈  Path: {RST}").strip()
            if not raw: return None
            return safe_path(raw)
    else:
        # Manual path
        print(f"\n  {DIM}  e.g: /storage/emulated/0/Download/file.txt{RST}")
        print(f"  {DIM}  Tip: Space wale names ke liye quotes use karo{RST}")
        print(f"  {DIM}  e.g: '/storage/emulated/0/My Files/test.txt'{RST}\n")
        raw = input(f"  {W}◈  {label} path: {RST}").strip()
        if not raw: return None
        return safe_path(raw)

def pause():
    try:
        input(f"\n{DIM}  ◈  Enter dabao wapis jaane ke liye  ◈{RST}")
    except KeyboardInterrupt:
        pass

def sep(c=DIM, n=50):
    print(f"  {c}{'─'*n}{RST}")

# ── Box Drawing (phone-safe, ANSI-aware) ────────────────────────
def _vis(s):
    plain = re.sub(r"\033\[[0-9;]*[mGKHFJ]", "", s)
    w = 0
    for ch in plain:
        cp = ord(ch)
        if (0x1F000 <= cp <= 0x1FFFF or 0x2600 <= cp <= 0x27BF
                or 0x2E80 <= cp <= 0x9FFF):
            w += 2
        else:
            w += 1
    return w

BW = 36

def _brow(text, bc=M):
    pad = max(0, BW - _vis(text))
    sp  = " " * pad
    sys.stdout.write(f"  {bc}║{RST}{text}{sp}{bc}║{RST}\n")

def _btop(bc=M): print(f"  {bc}╔{chr(9552)*BW}╗{RST}")
def _bmid(bc=M): print(f"  {bc}╠{chr(9552)*BW}╣{RST}")
def _bbot(bc=M): print(f"  {bc}╚{chr(9552)*BW}╝{RST}")

def draw_box(rows, width=None, color=M):
    _btop(color)
    for r in rows:
        if r == "div": _bmid(color)
        else: _brow(r, color)
    _bbot(color)

def feature_header(icon, name, sub="", others=""):
    print()
    _btop(M)
    _brow(f" {BLD}{C}{icon}{RST}  {BLD}{W}{name}{RST}", M)
    if sub: _brow(f"  {DIM}{sub}{RST}", M)
    if others:
        _bmid(M)
        _brow(f"  {DIM}{others}{RST}", M)
    _bbot(M)
    print()

OTHER_FEATURES = "Domain·Port·HTTP·SNI·Sub·Extract·JSON·IP·Net·Update"

# ================================================================
#  PROGRESS BAR  ── Single line, never scrolls
# ================================================================
_prog_lock = threading.Lock()

def draw_progress(done, total, saved, stopped=False):
    pct = int((done / total) * 22) if total else 0
    bar = f"{GR2}{'█'*pct}{DIM}{'░'*(22-pct)}{RST}"
    st  = f"{R}STOP{RST}" if stopped else f"{Y}SCAN{RST}"
    line = (f"  {DIM}[{RST}{bar}{DIM}]{RST} "
            f"{st} {GR2}{done}{DIM}/{RST}{total}  "
            f"{G}✔{RST}{GR2}{saved}{RST} saved")
    with _prog_lock:
        sys.stdout.write(f"{CR}{CL}{line}")
        sys.stdout.flush()

def print_result_line(line_str):
    """Print a result line above the progress bar"""
    with _prog_lock:
        sys.stdout.write(f"{CR}{CL}")
        sys.stdout.write(line_str + "\n")
        sys.stdout.flush()

# ================================================================
#  SAVE HELPER
# ================================================================
def save_prompt(data, name="scan_result.json"):
    try:
        ch = input(f"\n  {W}Save results? (y/n): {RST}").strip().lower()
        if ch != "y": return
        p = input(f"  {W}Path (Enter = ~/{name}): {RST}").strip()
        if not p: p = os.path.expanduser(f"~/{name}")
        with open(safe_path(p), "w") as f:
            json.dump(data, f, indent=2)
        print(f"  {G}✔ Saved → {p}{RST}")
    except KeyboardInterrupt:
        pass

# ================================================================
#  SERVER NAME LOOKUP
# ================================================================
CF_PREFIXES = [
    "172.65","104.16","104.21","103.21","103.22","141.101",
    "108.162","190.93","188.114","162.158","104.18","116.50",
    "104.19","104.20","172.64","198.41","197.234","188.114",
]
AKAMAI_PREFIXES = [
    "49.44","49.40","49.45","23.32","23.64","23.72",
    "96.6","96.7","184.24","184.25","184.26","184.27",
    "2.16","23.0","23.192","23.193","23.194","23.195",
]

def get_server_name(ip):
    for p in CF_PREFIXES:
        if ip.startswith(p): return "Cloudflare"
    for p in AKAMAI_PREFIXES:
        if ip.startswith(p): return "Akamai"
    known = {
        "45.123":"F5-BigIP","45.60":"F5-BigIP",
        "35.190":"Google","142.250":"Google","74.125":"Google",
        "172.217":"Google","216.58":"Google",
        "13.107":"Microsoft","20.":"Microsoft",
        "52.":"Amazon","54.":"Amazon","18.":"Amazon",
    }
    for prefix, name in known.items():
        if ip.startswith(prefix): return name
    return "Unknown"

def is_cloudflare(server):
    return "cloudflare" in server.lower()

# ================================================================
#  SNI CORE CONNECT
# ================================================================
def sni_connect(host, port, timeout, method="GET"):
    try:
        ip = socket.gethostbyname(host)
    except:
        return "-", "-", "Unknown"

    server = get_server_name(ip)
    code   = "-"

    # Build HTTP request
    if method == "POST":
        body     = ""
        req_line = (f"POST / HTTP/1.1\r\nHost: {host}\r\n"
                    f"User-Agent: Mozilla/5.0\r\n"
                    f"Content-Type: application/x-www-form-urlencoded\r\n"
                    f"Content-Length: 0\r\nConnection: close\r\n\r\n")
    elif method == "HEAD":
        req_line = (f"HEAD / HTTP/1.1\r\nHost: {host}\r\n"
                    f"User-Agent: Mozilla/5.0\r\nConnection: close\r\n\r\n")
    else:  # GET (default)
        req_line = (f"GET / HTTP/1.1\r\nHost: {host}\r\n"
                    f"User-Agent: Mozilla/5.0\r\n"
                    f"Accept: */*\r\nConnection: close\r\n\r\n")

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        s.connect((ip, port))

        if port == 443:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode    = ssl.CERT_NONE
            ss  = ctx.wrap_socket(s, server_hostname=host)
            ss.sendall(req_line.encode())
            raw = ss.recv(2048).decode("utf-8", errors="ignore")
            ss.close()
        else:
            s.sendall(req_line.encode())
            raw = s.recv(2048).decode("utf-8", errors="ignore")
            s.close()

        m = re.search(r"HTTP/[\d.]+ (\d+)", raw)
        if m: code = m.group(1)

        sm = re.search(r"[Ss]erver:\s*([^\r\n]+)", raw)
        if sm: server = sm.group(1).strip()[:15]

        return code, ip, server

    except socket.timeout:         return "TMO", ip, server
    except ConnectionRefusedError: return "REF", ip, server
    except ssl.SSLError:           return "SSL", ip, server
    except:                        return "-",   ip, server

# ================================================================
#  SNI FILTER
# ================================================================
def sni_keep(code, server):
    s  = str(code).strip()
    sv = server.strip().lower()
    if s in ["TMO","REF","SSL","-",""]: return False
    if s == "302":                       return False
    if "akamai" in sv:                   return False
    if sv in ["unknown","-",""]:         return False
    return True

# ================================================================
#  THREAD SELECTOR
# ================================================================
def select_threads():
    d  = DEFAULT_THREADS
    iw = 38
    draw_box([
        f"  {BLD}{W}Thread Selection{RST}",
        "div",
        f"  {G}[1]{RST} {W}10   {RST}{DIM}Low Device{RST}",
        f"  {G}[2]{RST} {W}30   {RST}{DIM}Mid Device{RST}",
        f"  {G}[3]{RST} {W}50   {RST}{DIM}High Device{RST}",
        f"  {G}[4]{RST} {W}100  {RST}{DIM}Very High{RST}",
        f"  {G}[5]{RST} {W}Custom{RST}",
        f"  {DIM}Enter = Auto ({d}t · {TIER}){RST}",
    ], iw, M)
    ch = input(f"\n  {W}◈  Choice: {RST}").strip()
    if ch == "":    return d
    elif ch == "1": return 10
    elif ch == "2": return 30
    elif ch == "3": return 50
    elif ch == "4": return 100
    elif ch == "5":
        try:
            n = int(input(f"  {W}Threads: {RST}").strip())
            return max(1, min(n, 500))
        except:
            return d
    return d

# ================================================================
#  ASCII ART  — Clean & Compact Slant Font (Forced Same Line)
# ================================================================
DEV_ART = [
    r"  _______________________",
    r"   / __ \  / ____/| |  / /",
    r"  / / / / / __/   | | / / ",
    r" / /_/ / / /___   | |/ /  ",
    r"/_____/ /_____/   |___/   "
]
DEV_COLORS = [CY2, C, LB, B, PU]

# TREX properly fixed with no gaps between letters
TREX_ART = [
    r" ____________________________",
    r"  /_  __// __ \ / ____/| |/ /",
    r"   / /  / /_/ // __/   |   / ",
    r"  / /  / _, _// /___  /   |  ",
    r" /_/  /_/|_| /_____/ /_/|_|  "
]
TREX_COLORS = [Y, Y, O, O, R]

def _art_print(animated=False):
    """Prints DEV and TREX merged perfectly onto the SAME line."""
    for i in range(5):
        dc = BLD + DEV_COLORS[i]
        tc = BLD + TREX_COLORS[i]
        # Force them side-by-side with minimal spacing for perfect fit
        line = f"  {dc}{DEV_ART[i]}{RST} {tc}{TREX_ART[i]}{RST}"
        
        if animated:
            sys.stdout.write(line + chr(10))
            sys.stdout.flush()
            time.sleep(0.04)
        else:
            print(line)

# ================================================================
#  STARTUP ANIMATION  — Typewriter, fast, no progress bar
# ================================================================
def startup_animation():
    clr()
    print()

    # Art appears line by line (animated=True)
    _art_print(animated=True)
    print()

    # Separator line types out
    sep_line = "  " + chr(9135)*36
    sys.stdout.write(M + sep_line + RST + chr(10))
    sys.stdout.flush()
    time.sleep(0.05)

    # Tool info typewriter (fast)
    info_lines = [
        f"  {BLD}{W}  ULTRA SCANNER {TOOL_VER}{RST}  {DIM}·  Bug Host Tool{RST}",
        f"  {DIM}  Device: {TIER}  |  Threads: {DEFAULT_THREADS}  |  T/O: {TIMEOUT}s{RST}",
    ]
    for line in info_lines:
        # Print char by char but very fast
        visible = re.sub(r"\033\[[0-9;]*m", "", line)
        sys.stdout.write(line + chr(10))
        sys.stdout.flush()
        time.sleep(0.05)

    sys.stdout.write(M + sep_line + RST + chr(10))
    sys.stdout.flush()
    time.sleep(0.3)
    clr()

# ================================================================
#  BANNER  (compact — shown on every menu/feature screen)
# ================================================================
def banner():
    online = is_online()
    tc = G if TIER=="HIGH" else Y if TIER=="MID" else R
    nc = G if online else R
    ns = "ONLINE  " + chr(10004) if online else "OFFLINE " + chr(10008)

    print(RST)
    print_banner_art(animated=False)

    _btop(M)
    _brow(f" {DIM}ULTRA SCANNER {TOOL_VER}  \u00b7  Bug Host Tool{RST}", M)
    _bmid(M)
    _brow(f" {tc}\u25cf {TIER}{RST}  {DIM}|{RST}  {nc}\u25cf {ns}{RST}  {DIM}| T:{DEFAULT_THREADS} | {TIMEOUT}s{RST}", M)
    _bbot(M)

# ================================================================
#  BANNER  — compact, always readable, italic+side-by-side
# ================================================================
def banner():
    online = is_online()
    tc = G if TIER=="HIGH" else Y if TIER=="MID" else R
    nc = G if online else R
    ns = "ONLINE  " + chr(10004) if online else "OFFLINE " + chr(10008)

    print(RST)
    _art_print(animated=False)
    print()

    _btop(M)
    _brow(f" {DIM}ULTRA SCANNER {TOOL_VER}  ·  Bug Host Tool{RST}", M)
    _bmid(M)
    _brow(f" {tc}● {TIER}{RST}  {DIM}|{RST}  {nc}● {ns}{RST}  {DIM}| T:{DEFAULT_THREADS} | {TIMEOUT}s{RST}", M)
    _bbot(M)

# ================================================================
#  MENU
# ================================================================
def menu():
    clr()
    banner()
    print()
    _btop(M)
    _brow(f"  {BLD}{W}" + chr(9670) + "  FEATURES  " + chr(9670) + f"{RST}", M)
    _bmid(M)
    _brow(f"  {G}[ 1]{RST}  Domain Scanner    {DIM}| Net{RST}", M)
    _brow(f"  {G}[ 2]{RST}  TCP Port Scanner  {DIM}| Local/Net{RST}", M)
    _brow(f"  {G}[ 3]{RST}  HTTP Info         {DIM}| Net{RST}", M)
    _brow(f"  {G}[ 4]{RST}  SNI Scanner       {Y}| Offline " + chr(10004) + f"{RST}", M)
    _brow(f"  {G}[ 5]{RST}  Subdomain Finder  {DIM}| Net{RST}", M)
    _brow(f"  {G}[ 6]{RST}  Extract Domains   {Y}| Offline " + chr(10004) + f"{RST}", M)
    _brow(f"  {G}[ 7]{RST}  Export JSON       {Y}| Offline " + chr(10004) + f"{RST}", M)
    _brow(f"  {G}[ 8]{RST}  IP Calculator     {Y}| Offline " + chr(10004) + f"{RST}", M)
    _brow(f"  {G}[ 9]{RST}  Network Scan      {Y}| WiFi " + chr(10004) + f"{RST}", M)
    _brow(f"  {G}[10]{RST}  Device Info       {Y}| Offline " + chr(10004) + f"{RST}", M)
    _bmid(M)
    _brow(f"  {G}[11]{RST}  Tunable Checker   {DIM}| Net{RST}", M)
    _bmid(M)
    _brow(f"  {C}[ U]{RST}  Update Tool       {DIM}| Net{RST}", M)
    _brow(f"  {R}[ 0]{RST}  Exit", M)
    _bbot(M)
    return input(f"\n  {W}> Select: {RST}").strip().lower()

# ================================================================
#  UPDATE TOOL
# ================================================================
def update_tool():
    clr(); banner()
    feature_header("🔄", "UPDATE TOOL",
                   "Downloads latest version from GitHub",
                   OTHER_FEATURES)

    if not is_online():
        print(f"  {R}✘  No internet! Update ke liye net chahiye.{RST}")
        return pause()

    # Find current script path
    script = os.path.abspath(__file__)
    print(f"  {G}✔{RST}  Current file  {DIM}│{RST}  {script}")
    print(f"  {G}✔{RST}  Source        {DIM}│{RST}  GitHub")
    print(f"\n  {Y}Downloading update...{RST}\n")

    try:
        result = subprocess.run(
            ["curl", "-L", "-o", script, TOOL_URL],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            print(f"  {GR2}✔  Update successful!{RST}")
            print(f"  {Y}  Tool restart karo: python {os.path.basename(script)}{RST}")
        else:
            print(f"  {R}✘  Update failed. curl error:{RST}")
            print(f"  {DIM}  {result.stderr[:100]}{RST}")
    except FileNotFoundError:
        # curl nahi hai, wget try karo
        try:
            result = subprocess.run(
                ["wget", "-O", script, TOOL_URL],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0:
                print(f"  {GR2}✔  Update successful! Restart karo.{RST}")
            else:
                print(f"  {R}✘  wget bhi fail hua.{RST}")
        except:
            print(f"  {R}✘  curl/wget dono nahi mile.{RST}")
            print(f"  {Y}  Run karo: pkg install curl -y{RST}")
    except Exception as e:
        print(f"  {R}✘  Error: {e}{RST}")

    pause()

# ================================================================
#  1. DOMAIN SCANNER
# ================================================================
def domain_scanner():
    clr(); banner()
    feature_header("🌐", "DOMAIN SCANNER",
                   "Net connection required",
                   OTHER_FEATURES)

    if not is_online():
        print(f"  {R}✘  No internet! Ye feature offline nahi chalta.{RST}")
        print(f"  {Y}   SNI Scanner try karo → [4]{RST}")
        return pause()

    target = input(f"  {W}◈  Domain / IP: {RST}").strip()
    if not target: return
    results = {"target": target, "time": str(datetime.now())}
    print(); sep(C)

    try:
        ip = socket.gethostbyname(target)
        results["ip"] = ip
        print(f"  {G}✔{RST}  IP Address    {DIM}│{RST}  {W}{ip}{RST}")
    except:
        print(f"  {R}✘  DNS resolve failed{RST}")
        ip = None

    if ip:
        try:
            rev = socket.gethostbyaddr(ip)[0]
            results["reverse_dns"] = rev
            print(f"  {G}✔{RST}  Reverse DNS   {DIM}│{RST}  {rev}")
        except:
            print(f"  {DIM}    Reverse DNS  │  N/A{RST}")
        try:
            all_ips = list({x[4][0] for x in socket.getaddrinfo(target, None)})
            results["all_ips"] = all_ips
            print(f"  {G}✔{RST}  All IPs       {DIM}│{RST}  {', '.join(all_ips)}")
        except:
            pass

    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode    = ssl.CERT_OPTIONAL
        conn = ctx.wrap_socket(
            socket.create_connection((target, 443), timeout=TIMEOUT),
            server_hostname=target)
        cert = conn.getpeercert(); conn.close()
        cn  = dict(x[0] for x in cert.get("subject",[])).get("commonName","N/A")
        exp = cert.get("notAfter","N/A")
        org = dict(x[0] for x in cert.get("issuer",[])).get("organizationName","N/A")
        results["ssl"] = {"cn":cn,"expiry":exp,"issuer":org}
        print(f"  {G}✔{RST}  SSL CN        {DIM}│{RST}  {cn}")
        print(f"  {G}✔{RST}  SSL Expiry    {DIM}│{RST}  {exp}")
        print(f"  {G}✔{RST}  SSL Issuer    {DIM}│{RST}  {org}")
    except:
        print(f"  {DIM}    SSL          │  Not available{RST}")

    try:
        import urllib.request
        for sc in ["https","http"]:
            try:
                req  = urllib.request.Request(f"{sc}://{target}",
                                              headers={"User-Agent":"Mozilla/5.0"})
                resp = urllib.request.urlopen(req, timeout=TIMEOUT)
                results["http_status"] = resp.status
                results["http_url"]    = resp.url
                print(f"  {G}✔{RST}  HTTP Status   {DIM}│{RST}  {resp.status}")
                print(f"  {G}✔{RST}  Final URL     {DIM}│{RST}  {resp.url}")
                break
            except: continue
    except: pass

    sep(C); save_prompt(results); pause()

# ================================================================
#  2. PORT SCANNER
# ================================================================
def _scan_port(host, port, to):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(to)
        r = s.connect_ex((host, port))
        s.close()
        return port if r == 0 else None
    except:
        return None

def port_scanner():
    clr(); banner()
    feature_header("⚡", "TCP PORT SCANNER",
                   "Works on local network without internet",
                   OTHER_FEATURES)

    target = input(f"  {W}◈  IP / Domain: {RST}").strip()
    if not target: return

    draw_box([
        f"  {BLD}{W}Port Range{RST}",
        "div",
        f"  {G}[1]{RST} {W}Common Ports {RST}{DIM}(Top 30){RST}",
        f"  {G}[2]{RST} {W}Full Range   {RST}{DIM}(1-1024){RST}",
        f"  {G}[3]{RST} {W}Custom Range{RST}",
        f"  {G}[4]{RST} {W}Single Port{RST}",
    ], 38, M)
    ch = input(f"\n  {W}◈  Choice: {RST}").strip()

    COMMON = [21,22,23,25,53,80,110,111,135,139,143,443,445,
              993,995,1723,3306,3389,5900,8080,8443,8888,
              9090,27017,6379,5432,1521,1433,2181]
    if ch=="1":   ports = COMMON
    elif ch=="2": ports = list(range(1,1025))
    elif ch=="3":
        try:
            r = input(f"  {W}Range (e.g. 1-500): {RST}").split("-")
            ports = list(range(int(r[0]),int(r[1])+1))
        except:
            print(f"  {R}Invalid range{RST}"); return pause()
    elif ch=="4":
        try: ports = [int(input(f"  {W}Port: {RST}").strip())]
        except: return pause()
    else: return

    threads = select_threads()
    try:
        ip = socket.gethostbyname(target)
    except:
        print(f"  {R}✘  DNS Failed{RST}"); return pause()

    total = len(ports)
    print(f"\n  {Y}Scanning {ip} — {total} ports — {threads} threads...{RST}")
    print(f"  {DIM}Ctrl+C to stop{RST}\n")

    open_ports = []
    done = 0
    lock = threading.Lock()
    stop = threading.Event()

    def worker(port):
        nonlocal done
        if stop.is_set(): return None
        result = _scan_port(ip, port, TIMEOUT)
        with lock:
            done += 1
            if done % 5 == 0 or done == total:
                draw_progress(done, total, len(open_ports))
        return result

    draw_progress(0, total, 0)
    try:
        with ThreadPoolExecutor(max_workers=threads) as ex:
            futures = {ex.submit(worker, p): p for p in ports}
            for f in as_completed(futures):
                r = f.result()
                if r:
                    with lock: open_ports.append(r)
    except KeyboardInterrupt:
        stop.set()
        draw_progress(done, total, len(open_ports), stopped=True)

    print(); sep(C)
    SVCS = {21:"FTP",22:"SSH",23:"Telnet",25:"SMTP",53:"DNS",
            80:"HTTP",110:"POP3",143:"IMAP",443:"HTTPS",445:"SMB",
            3306:"MySQL",3389:"RDP",5432:"PostgreSQL",6379:"Redis",
            8080:"HTTP-Alt",8443:"HTTPS-Alt",27017:"MongoDB",
            1433:"MSSQL",1521:"Oracle",8888:"HTTP-Alt",2181:"ZooKeeper"}

    if open_ports:
        open_ports.sort()
        print(f"\n  {G}{BLD}Open Ports: {len(open_ports)}{RST}\n")
        print(f"  {DIM}  Port      Service{RST}")
        sep(DIM, 26)
        for p in open_ports:
            print(f"  {G}✔{RST}  {Y}{str(p):<8}{RST}{C}{SVCS.get(p,'Unknown')}{RST}")
    else:
        print(f"\n  {R}No open ports found.{RST}")

    save_prompt({"target":target,"ip":ip,"open_ports":open_ports}); pause()

# ================================================================
#  3. HTTP INFO
# ================================================================
def http_info():
    clr(); banner()
    feature_header("🔍", "HTTP INFO","Net connection required", OTHER_FEATURES)

    if not is_online():
        print(f"  {R}✘  No internet!{RST}"); return pause()

    target = input(f"  {W}◈  Domain / URL: {RST}").strip()
    if not target: return
    urls = [target] if target.startswith("http") else [f"https://{target}",f"http://{target}"]

    import urllib.request
    print(); sep(C)
    for url in urls:
        try:
            req  = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"})
            resp = urllib.request.urlopen(req, timeout=TIMEOUT)
            h    = dict(resp.headers)
            print(f"  {G}✔{RST}  URL           {DIM}│{RST}  {resp.url}")
            print(f"  {G}✔{RST}  Status        {DIM}│{RST}  {resp.status}")
            print(f"  {G}✔{RST}  Server        {DIM}│{RST}  {h.get('server','N/A')}")
            print(f"  {G}✔{RST}  Content-Type  {DIM}│{RST}  {h.get('content-type','N/A')}")
            print(f"  {G}✔{RST}  Powered-By    {DIM}│{RST}  {h.get('x-powered-by','N/A')}")
            print(f"  {G}✔{RST}  CDN / Via     {DIM}│{RST}  {h.get('via',h.get('x-cdn','N/A'))}")
            print(f"  {G}✔{RST}  Cache         {DIM}│{RST}  {h.get('cache-control','N/A')}")
            print(f"  {G}✔{RST}  HSTS          {DIM}│{RST}  {h.get('strict-transport-security','N/A')}")
            save_prompt({"url":resp.url,"status":resp.status,"headers":h}); break
        except Exception as e:
            print(f"  {R}✘  {url} → {e}{RST}")
    sep(C); pause()

# ================================================================
#  4. SNI SCANNER  ◆ Main Feature
# ================================================================
def sni_scanner():
    clr(); banner()
    feature_header("🔒", "SNI SCANNER",
                   "Works WITHOUT internet · No recharge needed ✔",
                   OTHER_FEATURES)

    print(f"  {DIM}  Ctrl+C anytime to stop{RST}")
    in_path = ask_file_path("Subdomains file", ".txt")
    if not in_path: return
    if not os.path.exists(in_path):
        print(f"\n  {R}✘  File nahi mili: {in_path}{RST}"); return pause()

    with open(in_path,"r",errors="ignore") as f:
        raw = [l.strip() for l in f if l.strip() and not l.startswith("#")]

    domains = []
    for d in raw:
        d = re.sub(r"https?://","",d).split("/")[0].split(":")[0].strip()
        if d and "." in d: domains.append(d)
    domains = list(dict.fromkeys(domains))

    if not domains:
        print(f"\n  {R}✘  No valid domains found.{RST}"); return pause()

    folder   = os.path.dirname(in_path)
    base     = os.path.basename(in_path)
    out_path = os.path.join(folder, f"sni_{base}")

    # ── Port Selection ────────────────────────────────────────────
    draw_box([
        f"  {BLD}{W}Port Selection{RST}",
        "div",
        f"  {G}[1]{RST} {W}443 only  {RST}{Y}← Default (Faster){RST}",
        f"  {G}[2]{RST} {W}80 only{RST}",
        f"  {G}[3]{RST} {W}443 + 80  {RST}{DIM}(Both){RST}",
        f"  {DIM}Enter = 443 only{RST}",
    ], 38, M)
    pc = input(f"\n  {W}◈  Port: {RST}").strip()
    PORTS = [80] if pc=="2" else [443,80] if pc=="3" else [443]

    # ── HTTP Method ───────────────────────────────────────────────
    draw_box([
        f"  {BLD}{W}HTTP Method{RST}",
        "div",
        f"  {G}[1]{RST} {W}GET   {RST}{Y}← Default · Best Response{RST}",
        f"  {DIM}  Full body + headers milta hai{RST}",
        f"  {G}[2]{RST} {W}HEAD  {RST}{DIM}Fast · Sirf headers{RST}",
        f"  {G}[3]{RST} {W}POST  {RST}{DIM}Form submit method{RST}",
        f"  {DIM}Enter = GET{RST}",
    ], 38, M)
    mc = input(f"\n  {W}◈  Method: {RST}").strip()
    HTTP_METHOD = "HEAD" if mc=="2" else "POST" if mc=="3" else "GET"

    threads = select_threads()
    total   = len(domains) * len(PORTS)

    sep(C)
    print(f"  {G}✔{RST}  Domains   {DIM}│{RST}  {W}{len(domains)}{RST}")
    print(f"  {G}✔{RST}  Ports     {DIM}│{RST}  {W}{', '.join(map(str,PORTS))}{RST}")
    print(f"  {G}✔{RST}  Method    {DIM}│{RST}  {Y}{HTTP_METHOD}{RST}")
    print(f"  {G}✔{RST}  Threads   {DIM}│{RST}  {W}{threads}{RST}")
    print(f"  {G}✔{RST}  Total     {DIM}│{RST}  {W}{total} checks{RST}")
    print(f"  {G}✔{RST}  Output    {DIM}│{RST}  {W}{out_path}{RST}")
    sep(C)

    # Table header
    print(f"\n  {BLD}{W}{'Code':<6}{DIM}│{RST}{BLD}{W} {'IP':<16}{DIM}│{RST}{BLD}{W} {'Server':<15}{DIM}│{RST}{BLD}{W} Host{RST}")
    print(f"  {DIM}{'─'*5}─┼─{'─'*15}─┼─{'─'*14}─┼─{'─'*20}{RST}")

    try:
        out_f = open(out_path,"w",buffering=1,encoding="utf-8")
    except Exception as e:
        print(f"\n  {R}✘  Cannot create output: {e}{RST}"); return pause()

    out_f.write(f"# —͟͞⛦⃕͜᪾ 𝐃𝐄𝐕࿐ & T-REX — SNI SCAN\n")
    out_f.write(f"# Date   : {datetime.now()}\n")
    out_f.write(f"# Source : {in_path}\n")
    out_f.write(f"# Ports  : {PORTS}\n")
    out_f.write(f"# Method : {HTTP_METHOD}\n\n")
    out_f.write(f"{'Code':<6}| {'IP':<16}| {'Server':<15}| Host\n")
    out_f.write(f"{'─'*6}+{'─'*17}+{'─'*16}+{'─'*30}\n")

    done  = 0
    saved = 0
    lock  = threading.Lock()
    stop  = threading.Event()

    print()
    draw_progress(0, total, 0)

    def worker(domain, port):
        nonlocal done, saved
        if stop.is_set(): return

        code, ip, server = sni_connect(domain, port, TIMEOUT, HTTP_METHOD)
        keep = sni_keep(code, server)

        with lock:
            done += 1

            if keep:
                saved += 1
                cs  = str(code)[:5].ljust(5)
                ips = str(ip)[:15].ljust(15)
                svs = str(server)[:14].ljust(14)
                hst = f"{domain}:{port}"

                # ── Cloudflare = bright green ──
                sv_low = server.lower()
                if "cloudflare" in sv_low:
                    cc = GR2   # bright green
                elif str(code) in ["200","204"]:
                    cc = G
                elif str(code) in ["301","303","307","308"]:
                    cc = C
                elif str(code) in ["401","403"]:
                    cc = Y
                elif str(code) in ["400","404"]:
                    cc = O
                elif str(code).startswith("5"):
                    cc = R
                else:
                    cc = W

                line = f"  {cc}{cs}{RST}{DIM}│{RST}{ips} {DIM}│{RST}{svs} {DIM}│{RST} {hst}"
                print_result_line(line)
                out_f.write(f"{str(code):<6}| {str(ip):<16}| {str(server):<15}| {hst}\n")
                out_f.flush()

            # Update progress — throttled: every 3 or on save or on finish
            if done % 3 == 0 or done == total or keep:
                draw_progress(done, total, saved)

    try:
        with ThreadPoolExecutor(max_workers=threads) as ex:
            futures = [ex.submit(worker,d,p) for d in domains for p in PORTS]
            for f in as_completed(futures): pass
    except KeyboardInterrupt:
        stop.set()
        draw_progress(done, total, saved, stopped=True)

    out_f.write(f"\n{'─'*60}\n")
    out_f.write(f"# Scanned : {done}\n# Saved   : {saved}\n")
    out_f.write(f"# Done    : {datetime.now()}\n")
    out_f.close()

    print(); sep(C)
    st = f"{R}STOPPED{RST}" if stop.is_set() else f"{GR2}COMPLETE{RST}"
    print(f"\n  {BLD}Status    {DIM}│{RST}  {st}")
    print(f"  {G}✔{RST}  Scanned  {DIM}│{RST}  {done}/{total}")
    print(f"  {G}✔{RST}  Saved    {DIM}│{RST}  {saved}")
    print(f"  {G}✔{RST}  Output   {DIM}│{RST}  {out_path}")
    sep(C); pause()

# ================================================================
# ================================================================
#  5. SUBDOMAIN FINDER  — NEXA-style Fast Queue + Passive APIs
#  No wordlist — Pure passive API discovery + fast DNS verify
# ================================================================
import urllib.request as _ur
from queue import Queue as _Queue

def _api_get(url, timeout=8):
    """Simple HTTP GET for passive API queries"""
    try:
        req = _ur.Request(url, headers={
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json, text/html, */*"
        })
        return _ur.urlopen(req, timeout=timeout).read().decode("utf-8", errors="ignore")
    except:
        return None

def _sub_clean(d, base):
    """Validate and clean a subdomain"""
    d = re.sub(r"^\*\.", "", d.strip().lower())
    d = re.sub(r"https?://", "", d).split("/")[0].split(":")[0]
    if not d: return None
    if not (d.endswith(f".{base}") or d == base): return None
    if not re.match(r"^[a-z0-9.\-]+$", d): return None
    return d

# ── Passive API Sources ─────────────────────────────────────────
def _api_crt(domain):
    s = set()
    raw = _api_get(f"https://crt.sh/?q=%.{domain}&output=json", 12)
    if raw:
        try:
            for e in json.loads(raw):
                for n in e.get("name_value","").split("\n"):
                    c = _sub_clean(n, domain)
                    if c: s.add(c)
        except: pass
    return s

def _api_hackertarget(domain):
    s = set()
    raw = _api_get(f"https://api.hackertarget.com/hostsearch/?q={domain}", 8)
    if raw and "error" not in raw.lower() and "API" not in raw:
        for line in raw.splitlines():
            p = line.split(",")
            if p:
                c = _sub_clean(p[0], domain)
                if c: s.add(c)
    return s

def _api_alienvault(domain):
    s = set()
    raw = _api_get(
        f"https://otx.alienvault.com/api/v1/indicators/domain/{domain}/passive_dns", 8)
    if raw:
        try:
            for e in json.loads(raw).get("passive_dns", []):
                c = _sub_clean(e.get("hostname",""), domain)
                if c: s.add(c)
        except: pass
    return s

def _api_rapiddns(domain):
    s = set()
    raw = _api_get(f"https://rapiddns.io/subdomain/{domain}?full=1&down=1", 8)
    if raw:
        for m in re.findall(r"([a-zA-Z0-9\-.]+\." + re.escape(domain) + r")", raw):
            c = _sub_clean(m, domain)
            if c: s.add(c)
    return s

def _api_bufferover(domain):
    s = set()
    raw = _api_get(f"https://dns.bufferover.run/dns?q=.{domain}", 6)
    if raw:
        try:
            data = json.loads(raw)
            for e in data.get("FDNS_A", []) + data.get("RDNS", []):
                for p in e.split(","):
                    c = _sub_clean(p, domain)
                    if c: s.add(c)
        except: pass
    return s

def _api_urlscan(domain):
    s = set()
    raw = _api_get(
        f"https://urlscan.io/api/v1/search/?q=domain:{domain}&size=200", 8)
    if raw:
        try:
            for r in json.loads(raw).get("results", []):
                pg = r.get("page", {})
                for k in ["domain", "ptr"]:
                    c = _sub_clean(pg.get(k, ""), domain)
                    if c: s.add(c)
        except: pass
    return s

# ── Additional API Sources ─────────────────────────────────────
def _api_threatcrowd(domain):
    s = set()
    raw = _api_get(f"https://www.threatcrowd.org/searchApi/v2/domain/report/?domain={domain}", 8)
    if raw:
        try:
            data = json.loads(raw)
            for sub in data.get("subdomains", []):
                c = _sub_clean(sub, domain)
                if c: s.add(c)
        except: pass
    return s

def _api_certspotter(domain):
    s = set()
    raw = _api_get(
        f"https://api.certspotter.com/v1/issuances?domain={domain}&include_subdomains=true&expand=dns_names", 8)
    if raw:
        try:
            for entry in json.loads(raw):
                for name in entry.get("dns_names", []):
                    c = _sub_clean(name, domain)
                    if c: s.add(c)
        except: pass
    return s

def _api_anubis(domain):
    s = set()
    raw = _api_get(f"https://jldc.me/anubis/subdomains/{domain}", 8)
    if raw:
        try:
            for sub in json.loads(raw):
                c = _sub_clean(sub, domain)
                if c: s.add(c)
        except: pass
    return s

def _api_webarchive(domain):
    s = set()
    raw = _api_get(
        f"http://web.archive.org/cdx/search/cdx?url=*.{domain}&output=json&fl=original&collapse=urlkey&limit=500", 10)
    if raw:
        try:
            for row in json.loads(raw)[1:]:  # skip header
                url = row[0] if row else ""
                m = re.match(r"https?://([^/]+)", url)
                if m:
                    c = _sub_clean(m.group(1), domain)
                    if c: s.add(c)
        except: pass
    return s

def _api_riddler(domain):
    s = set()
    raw = _api_get(f"https://riddler.io/search/exportcsv?q=pld:{domain}", 8)
    if raw:
        for line in raw.splitlines():
            parts = line.split(",")
            if len(parts) >= 5:
                c = _sub_clean(parts[4], domain)
                if c: s.add(c)
    return s

def _api_c99(domain):
    s = set()
    raw = _api_get(f"https://subdomainfinder.c99.nl/scans/{domain}", 8)
    if raw:
        for m in re.findall(r"([a-zA-Z0-9.-]+" + re.escape("." + domain) + r")", raw):
            c = _sub_clean(m, domain)
            if c: s.add(c)
    return s

# ── Extra API Sources ───────────────────────────────────────────
def _api_threatminer(domain):
    s = set()
    raw = _api_get(f"https://api.threatminer.org/v2/domain.php?q={domain}&rt=5", 8)
    if raw:
        try:
            for sub in json.loads(raw).get("results", []):
                c = _sub_clean(sub, domain)
                if c: s.add(c)
        except: pass
    return s

def _api_omnisint(domain):
    s = set()
    raw = _api_get(f"https://sonar.omnisint.io/subdomains/{domain}", 8)
    if raw:
        try:
            for sub in json.loads(raw):
                c = _sub_clean(sub, domain)
                if c: s.add(c)
        except: pass
    return s

def _api_virustotal(domain):
    s = set()
    raw = _api_get(
        f"https://www.virustotal.com/ui/domains/{domain}/subdomains?limit=40", 6)
    if raw:
        try:
            data = json.loads(raw)
            for item in data.get("data", []):
                c = _sub_clean(item.get("id",""), domain)
                if c: s.add(c)
        except: pass
    return s

def _api_dnsdumpster(domain):
    """DNSdumpster via hackertarget endpoint (no CSRF needed)"""
    s = set()
    raw = _api_get(f"https://api.hackertarget.com/dnslookup/?q={domain}", 8)
    if raw and "error" not in raw.lower():
        for m in re.findall(r"([a-zA-Z0-9.-]+" + re.escape("." + domain) + r")", raw):
            c = _sub_clean(m, domain)
            if c: s.add(c)
    return s

def _api_securitytrails_free(domain):
    """SecurityTrails free HTML scrape"""
    s = set()
    raw = _api_get(f"https://securitytrails.com/list/apex_domain/{domain}", 6)
    if raw:
        for m in re.findall(r"([a-zA-Z0-9.-]+" + re.escape("." + domain) + r")", raw):
            c = _sub_clean(m, domain)
            if c: s.add(c)
    return s

API_SOURCES = [
    ("crt.sh",        _api_crt),
    ("HackerTarget",  _api_hackertarget),
    ("AlienVault",    _api_alienvault),
    ("RapidDNS",      _api_rapiddns),
    ("BufferOver",    _api_bufferover),
    ("URLScan",       _api_urlscan),
    ("ThreatCrowd",   _api_threatcrowd),
    ("CertSpotter",   _api_certspotter),
    ("Anubis",        _api_anubis),
    ("WebArchive",    _api_webarchive),
    ("Riddler",       _api_riddler),
    ("C99",           _api_c99),
    ("ThreatMiner",   _api_threatminer),
    ("Omnisint",      _api_omnisint),
    ("VirusTotal",    _api_virustotal),
    ("DNSDumpster",   _api_dnsdumpster),
    ("SecurityTrails",_api_securitytrails_free),
]

def subdomain_finder():
    clr(); banner()
    feature_header("🔎", "SUBDOMAIN FINDER",
                   "Passive APIs + Fast Queue DNS verify · No wordlist",
                   OTHER_FEATURES)

    if not is_online():
        print(f"  {R}✘  No internet connection!{RST}")
        return pause()

    print(f"  {DIM}  Ctrl+C anytime to stop{RST}")
    in_path = ask_file_path("Domains file", ".txt")
    if not in_path: return
    if not os.path.exists(in_path):
        print(f"  {R}✘  File not found: {in_path}{RST}"); return pause()

    with open(in_path, "r", errors="ignore") as f:
        base_domains = list(dict.fromkeys([
            re.sub(r"https?://","",l.strip()).split("/")[0].strip()
            for l in f if l.strip() and not l.startswith("#") and "." in l
        ]))

    if not base_domains:
        print(f"  {R}✘  No valid domains found.{RST}"); return pause()

    folder   = os.path.dirname(in_path)
    base_n   = os.path.splitext(os.path.basename(in_path))[0]
    out_path = os.path.join(folder, f"{base_n}_subdomains.txt")

    print(f"\n  {G}✔{RST}  Domains   {DIM}│{RST}  {W}{len(base_domains)}{RST}")
    print(f"  {G}✔{RST}  APIs      {DIM}│{RST}  {W}{len(API_SOURCES)} sources{RST}")
    print(f"  {G}✔{RST}  Output    {DIM}│{RST}  {W}{out_path}{RST}")
    print(f"  {DIM}  Sources: {", ".join(s[0] for s in API_SOURCES)}{RST}\n")
    sep(C)

    out_f = open(out_path, "w", buffering=1, encoding="utf-8")
    out_f.write(f"# DEV & T-REX — Subdomain Discovery\n")
    out_f.write(f"# Source: {in_path} | Date: {datetime.now()}\n\n")

    all_found   = set()
    total_saved = 0
    file_lock   = threading.Lock()
    stop        = threading.Event()

    def save_sub(sub):
        nonlocal total_saved
        with file_lock:
            if sub not in all_found:
                all_found.add(sub)
                total_saved += 1
                out_f.write(sub + "\n")
                out_f.flush()
                return True
        return False

    # NEXA-style Queue worker for fast DNS verification
    def dns_worker(q_in, domain, results):
        while True:
            sub = q_in.get()
            if sub is None:
                q_in.task_done()
                break
            try:
                socket.setdefaulttimeout(2.0)
                socket.gethostbyname(sub)
                results.append(sub)
            except:
                pass
            q_in.task_done()

    def process_domain(base):
        if stop.is_set(): return 0

        # Phase 1: Query ALL passive APIs concurrently
        collected = {base}
        with ThreadPoolExecutor(max_workers=len(API_SOURCES)) as ex:
            futures = {ex.submit(fn, base): nm for nm, fn in API_SOURCES}
            for fut in as_completed(futures):
                try:
                    collected.update(fut.result() or set())
                except: pass

        # Phase 2: NEXA-style Queue + 100 threads DNS verify (FAST)
        to_check = [s for s in collected if s not in all_found]
        verified = []

        if to_check:
            q    = _Queue()
            n_threads = min(150, max(50, len(to_check)))
            workers  = []

            for _ in range(n_threads):
                t = threading.Thread(
                    target=dns_worker,
                    args=(q, base, verified),
                    daemon=True
                )
                t.start()
                workers.append(t)

            for sub in to_check:
                if stop.is_set(): break
                q.put(sub)

            for _ in range(n_threads):
                q.put(None)

            q.join()
            for t in workers:
                t.join()

        # Always include base domain
        if base not in all_found:
            verified.append(base)

        # Phase 3: Save results
        new_count = 0
        for sub in sorted(verified):
            if save_sub(sub):
                new_count += 1

        return new_count, verified

    # Process all domains — 2 concurrently to respect API rate limits
    done_d = 0
    total_d = len(base_domains)

    try:
        with ThreadPoolExecutor(max_workers=2) as dom_ex:
            fut_map = {dom_ex.submit(process_domain, b): b for b in base_domains}

            for fut in as_completed(fut_map):
                if stop.is_set(): break
                base = fut_map[fut]
                done_d += 1
                try:
                    n, subs = fut.result()
                    # Print found subdomains
                    for sub in sorted(subs):
                        if sub != base:
                            print(f"  {G}✔{RST}  {sub}")
                    print(f"  {C}►{RST}  {base:<35} "
                          f"{G}{n} found{RST}  "
                          f"{DIM}[{done_d}/{total_d}] total:{total_saved}{RST}")
                except KeyboardInterrupt:
                    stop.set(); break
                except Exception as e:
                    print(f"  {R}✘{RST}  {base}  error: {e}")

    except KeyboardInterrupt:
        stop.set()

    out_f.write(f"\n# Total: {total_saved} | Done: {datetime.now()}\n")
    out_f.close()

    print(); sep(C)
    st = f"{R}STOPPED{RST}" if stop.is_set() else f"{GR2}COMPLETE{RST}"
    print(f"\n  Status   {DIM}│{RST}  {st}")
    print(f"  {G}✔{RST}  Found    {DIM}│{RST}  {total_saved} unique subdomains")
    print(f"  {G}✔{RST}  Output   {DIM}│{RST}  {out_path}")
    print(f"\n  {Y}  Next → SNI Scanner [4]{RST}")
    sep(C); pause()


# ================================================================
#  6. EXTRACT DOMAINS
# ================================================================
def extract_domains():
    clr(); banner()
    feature_header("📄", "EXTRACT DOMAINS","Offline ✔", OTHER_FEATURES)

    in_path = ask_file_path("Input file", "*")
    if not in_path: return
    if not os.path.exists(in_path):
        print(f"\n  {R}✘  File nahi mili{RST}"); return pause()

    with open(in_path,"r",errors="ignore") as f:
        content = f.read()

    pattern = r"(?:https?://)?(?:www\.)?([a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z]{2,})+)"
    domains = sorted(set(re.findall(pattern, content)))

    if not domains:
        print(f"\n  {R}✘  Koi domain nahi mila.{RST}"); return pause()

    folder   = os.path.dirname(in_path)
    out_path = os.path.join(folder, "extracted_domains.txt")

    with open(out_path,"w") as f:
        f.write(f"# —͟͞⛦⃕͜᪾ 𝐃𝐄𝐕࿐ & T-REX — Extracted\n")
        f.write(f"# Source: {in_path}\n# Date: {datetime.now()}\n\n")
        for d in domains: f.write(d+"\n")

    print(f"\n  {G}✔{RST}  Extracted  {DIM}│{RST}  {len(domains)} domains")
    print(f"  {G}✔{RST}  Saved      {DIM}│{RST}  {out_path}")
    print(f"\n  {DIM}Preview:{RST}")
    for d in domains[:10]: print(f"  {C}  {d}{RST}")
    if len(domains)>10: print(f"  {DIM}  ...+{len(domains)-10} more{RST}")
    pause()

# ================================================================
#  7. EXPORT JSON
# ================================================================
def export_json():
    clr(); banner()
    feature_header("💾", "EXPORT JSON","Convert .txt → JSON · Offline ✔", OTHER_FEATURES)

    in_path = ask_file_path("Input .txt file", ".txt")
    if not in_path: return
    if not os.path.exists(in_path):
        print(f"\n  {R}✘  File nahi mili{RST}"); return pause()

    with open(in_path,"r",errors="ignore") as f:
        lines = [l.strip() for l in f if l.strip() and not l.startswith("#")]

    data = {
        "tool": "—͟͞⛦⃕͜᪾ 𝐃𝐄𝐕࿐ & T-REX Ultra Scanner v3.1",
        "source": in_path, "exported": str(datetime.now()),
        "total": len(lines), "entries": lines
    }
    folder   = os.path.dirname(in_path)
    base     = os.path.splitext(os.path.basename(in_path))[0]
    out_path = os.path.join(folder, f"{base}.json")

    with open(out_path,"w") as f: json.dump(data,f,indent=2)
    print(f"\n  {G}✔{RST}  Entries  {DIM}│{RST}  {len(lines)}")
    print(f"  {G}✔{RST}  Saved    {DIM}│{RST}  {out_path}")
    pause()

# ================================================================
#  8. IP CALCULATOR
# ================================================================
def ip_calculator():
    clr(); banner()
    feature_header("🖥", "IP CALCULATOR","Subnet calculator · Offline ✔", OTHER_FEATURES)

    inp = input(f"  {W}◈  IP/CIDR (e.g. 192.168.1.0/24): {RST}").strip()
    if not inp: return
    try:
        net = ipaddress.ip_network(inp, strict=False)
        print(); sep(C)
        print(f"  {G}✔{RST}  Network     {DIM}│{RST}  {net.network_address}")
        print(f"  {G}✔{RST}  Broadcast   {DIM}│{RST}  {net.broadcast_address}")
        print(f"  {G}✔{RST}  Netmask     {DIM}│{RST}  {net.netmask}")
        print(f"  {G}✔{RST}  Hostmask    {DIM}│{RST}  {net.hostmask}")
        print(f"  {G}✔{RST}  Prefix      {DIM}│{RST}  /{net.prefixlen}")
        print(f"  {G}✔{RST}  Total IPs   {DIM}│{RST}  {net.num_addresses}")
        print(f"  {G}✔{RST}  Usable IPs  {DIM}│{RST}  {max(0,net.num_addresses-2)}")
        print(f"  {G}✔{RST}  Version     {DIM}│{RST}  IPv{net.version}")
        print(f"  {G}✔{RST}  Private     {DIM}│{RST}  {net.is_private}")
        hosts = list(net.hosts())
        if hosts:
            print(f"\n  {DIM}Host Range:{RST}")
            print(f"  {C}  {hosts[0]}  →  {hosts[-1]}{RST}")
        sep(C)
    except Exception as e:
        print(f"\n  {R}✘  Invalid: {e}{RST}")
    pause()

# ================================================================
#  9. LOCAL NETWORK SCAN
# ================================================================
def local_network_scan():
    clr(); banner()
    feature_header("📡", "LOCAL NETWORK SCAN",
                   "Scan WiFi devices · No internet needed ✔",
                   OTHER_FEATURES)

    try:
        s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        s.connect(("8.8.8.8",80))
        local_ip = s.getsockname()[0]; s.close()
    except:
        local_ip = "192.168.1.100"

    net_base = ".".join(local_ip.split(".")[:3])
    print(f"  {G}✔{RST}  Your IP   {DIM}│{RST}  {local_ip}")
    print(f"  {G}✔{RST}  Scanning  {DIM}│{RST}  {net_base}.1 → {net_base}.254")
    print(f"  {DIM}  Ctrl+C to stop{RST}\n")

    threads = select_threads()
    found   = []
    done    = 0
    lock    = threading.Lock()
    stop    = threading.Event()

    draw_progress(0,254,0)

    def ping_host(i):
        nonlocal done
        if stop.is_set(): return
        ip = f"{net_base}.{i}"
        alive = False
        for port in [80,443,22,8080,53]:
            try:
                s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                s.settimeout(0.5)
                if s.connect_ex((ip,port))==0: alive=True; s.close(); break
                s.close()
            except: pass
        with lock:
            done += 1
            if alive:
                try: hostname = socket.gethostbyaddr(ip)[0]
                except: hostname = "Unknown"
                found.append({"ip":ip,"hostname":hostname})
                print_result_line(f"  {G}✔{RST}  {ip:<18}  {C}{hostname}{RST}")
            if done%5==0 or done==254:
                draw_progress(done,254,len(found))

    try:
        with ThreadPoolExecutor(max_workers=threads) as ex:
            futures = [ex.submit(ping_host,i) for i in range(1,255)]
            for f in as_completed(futures): pass
    except KeyboardInterrupt:
        stop.set()
        draw_progress(done,254,len(found),stopped=True)

    print(); sep(C)
    print(f"\n  {G}✔{RST}  Devices found  {DIM}│{RST}  {len(found)}")
    save_prompt({"network":f"{net_base}.0/24","devices":found},"local_scan.json")
    pause()

# ================================================================
#  10. DEVICE INFO
# ================================================================
def device_info():
    clr(); banner()
    feature_header("📱","DEVICE INFO","System information · Offline ✔", OTHER_FEATURES)

    import platform
    print(); sep(C)
    print(f"  {G}✔{RST}  OS            {DIM}│{RST}  {platform.system()} {platform.release()}")
    print(f"  {G}✔{RST}  Architecture  {DIM}│{RST}  {platform.machine()}")
    print(f"  {G}✔{RST}  Python        {DIM}│{RST}  {platform.python_version()}")
    print(f"  {G}✔{RST}  Tool Version  {DIM}│{RST}  {TOOL_VER}")
    print(f"  {G}✔{RST}  Device Tier   {DIM}│{RST}  {TIER}")
    print(f"  {G}✔{RST}  Def.Threads   {DIM}│{RST}  {DEFAULT_THREADS}")
    print(f"  {G}✔{RST}  Timeout       {DIM}│{RST}  {TIMEOUT}s")
    try:
        rt=av=0
        with open("/proc/meminfo") as f:
            for line in f:
                if "MemTotal"     in line: rt=int(line.split()[1])//1024
                if "MemAvailable" in line: av=int(line.split()[1])//1024
        print(f"  {G}✔{RST}  RAM Total     {DIM}│{RST}  {rt} MB")
        print(f"  {G}✔{RST}  RAM Free      {DIM}│{RST}  {av} MB")
    except: pass
    try:
        import multiprocessing
        print(f"  {G}✔{RST}  CPU Cores     {DIM}│{RST}  {multiprocessing.cpu_count()}")
    except: pass
    try:
        with open("/proc/cpuinfo") as f:
            for line in f:
                if "Hardware" in line:
                    print(f"  {G}✔{RST}  Hardware      {DIM}│{RST}  {line.split(':')[1].strip()}"); break
    except: pass
    try:
        r = subprocess.run(["ip","addr"],capture_output=True,text=True,timeout=2)
        ips = re.findall(r"inet (\d+\.\d+\.\d+\.\d+)",r.stdout)
        if ips: print(f"  {G}✔{RST}  Local IPs     {DIM}│{RST}  {', '.join(ips)}")
    except: pass
    sep(C); pause()

# ================================================================
#  11. TUNABLE CHECKER  (from NEXA)
#  Checks if a domain/SNI is tunable for SSH tunneling
# ================================================================

NON_TUNABLE_IPS = ["23.", "49.", "184."]
TUNABLE_SERVERS = [
    "Cloudflare","CloudFront","Google","Fastly","Cachefly",
    "Bunny","Tengine","Sucuri","Gcore","Imperva","Tencent"
]

def _tc_detect_server(domain, ip):
    """
    Detect CDN/server using 3 methods:
    1. IP-range based detection (most reliable, works offline)
    2. Raw TCP SNI connect → parse Server header
    3. urllib HTTP request headers
    Returns server name string.
    """
    # Method 1: IP-based detection (instant, always works)
    ip_server = None
    CF_RANGES = ["172.65","104.16","104.21","104.18","104.19","104.20",
                 "103.21","103.22","141.101","108.162","190.93","188.114",
                 "162.158","172.64","198.41","197.234","116.50","104.17",
                 "103.31","141.101","188.114","190.93","197.234","198.41"]
    AK_RANGES = ["49.44","49.40","49.45","23.32","23.64","23.72",
                 "96.6","96.7","184.24","184.25","184.26","184.27",
                 "2.16","23.0","23.192","23.193","23.194","23.195"]
    for p in CF_RANGES:
        if ip.startswith(p): ip_server = "Cloudflare"; break
    if not ip_server:
        for p in AK_RANGES:
            if ip.startswith(p): ip_server = "Akamai"; break
    if not ip_server:
        if ip.startswith("35.190") or ip.startswith("142.250") or ip.startswith("74.125"):
            ip_server = "Google"
        elif ip.startswith("13.107") or ip.startswith("20."):
            ip_server = "Microsoft"
        elif ip.startswith("45.123") or ip.startswith("45.60"):
            ip_server = "F5/BigIP"

    # Method 2: Raw TCP SNI connect → get Server header
    tcp_server = None
    for port in [443, 80]:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(5)
            s.connect((ip, port))
            if port == 443:
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                ss = ctx.wrap_socket(s, server_hostname=domain)
                req = (f"GET / HTTP/1.1\r\nHost: {domain}\r\n"
                       f"User-Agent: Mozilla/5.0\r\nConnection: close\r\n\r\n")
                ss.sendall(req.encode())
                raw = b""
                try:
                    while len(raw) < 4096:
                        chunk = ss.recv(1024)
                        if not chunk: break
                        raw += chunk
                        if b"\r\n\r\n" in raw: break
                except: pass
                try: ss.close()
                except: pass
            else:
                req = (f"GET / HTTP/1.1\r\nHost: {domain}\r\n"
                       f"User-Agent: Mozilla/5.0\r\nConnection: close\r\n\r\n")
                s.sendall(req.encode())
                raw = b""
                try:
                    while len(raw) < 4096:
                        chunk = s.recv(1024)
                        if not chunk: break
                        raw += chunk
                        if b"\r\n\r\n" in raw: break
                except: pass
                try: s.close()
                except: pass

            text = raw.decode("utf-8", errors="ignore").lower()
            # Check for CDN signatures in response
            if "cf-ray" in text or "cf-cache-status" in text or "cloudflare" in text:
                tcp_server = "Cloudflare"; break
            if "x-amz-cf" in text or "cloudfront" in text:
                tcp_server = "CloudFront"; break
            sm = re.search(r"server:\s*([^\r\n]+)", text)
            if sm:
                sv = sm.group(1).strip()
                if "google" in sv or "gfe" in sv: tcp_server = "Google"; break
                if "fastly" in sv or "varnish" in sv: tcp_server = "Fastly"; break
                if "tengine" in sv: tcp_server = "Tengine"; break
                if "cloudflare" in sv: tcp_server = "Cloudflare"; break
            if "x-fastly" in text or "fastly" in text: tcp_server = "Fastly"; break
            if "x-gcore" in text or "gcdn" in text: tcp_server = "Gcore"; break
            if "x-imperva" in text or "incapsula" in text: tcp_server = "Imperva"; break
            if "x-sucuri" in text: tcp_server = "Sucuri"; break
            if "x-bunny" in text or "bunnycdn" in text: tcp_server = "Bunny"; break
        except:
            continue

    # Method 3: urllib request (catches redirects + more headers)
    url_server = None
    import urllib.request as _ur3
    for scheme in ["https", "http"]:
        try:
            import ssl as _ssl3
            ctx3 = _ssl3.create_default_context()
            ctx3.check_hostname = False
            ctx3.verify_mode = _ssl3.CERT_NONE
            req = _ur3.Request(f"{scheme}://{domain}",
                               headers={"User-Agent":"Mozilla/5.0"})
            if scheme == "https":
                resp = _ur3.urlopen(req, timeout=6, context=ctx3)
            else:
                resp = _ur3.urlopen(req, timeout=6)
            hdrs = str({k.lower(): v.lower() for k, v in resp.headers.items()})
            if "cf-ray" in hdrs or "cloudflare" in hdrs: url_server = "Cloudflare"; break
            if "x-amz-cf" in hdrs or "cloudfront" in hdrs: url_server = "CloudFront"; break
            if "x-fastly" in hdrs or "fastly" in hdrs: url_server = "Fastly"; break
            if "x-gcore" in hdrs: url_server = "Gcore"; break
            if "x-imperva" in hdrs or "incapsula" in hdrs: url_server = "Imperva"; break
            if "x-sucuri" in hdrs: url_server = "Sucuri"; break
            if "x-bunny" in hdrs or "bunnycdn" in hdrs: url_server = "Bunny"; break
            if "tengine" in hdrs or "alibaba" in hdrs: url_server = "Tengine"; break
            if "tencent-cdn" in hdrs: url_server = "Tencent"; break
        except:
            continue

    # Priority: tcp_server > url_server > ip_server > Unknown
    # TCP and URL are more accurate (actual response headers)
    final = tcp_server or url_server or ip_server or "Unknown"
    return final, ip_server, tcp_server, url_server

def _tc_is_tunable(ip, server):
    """
    TUNABLE if:
    1. Server is in TUNABLE_SERVERS list
    2. IP does NOT start with 23., 49., or 184.
    Both must be true.
    """
    matched = None
    for ts in TUNABLE_SERVERS:
        if ts.lower() in server.lower():
            matched = ts
            break

    if not matched:
        return False, f"Server '{server}' not in tunable CDN list", None

    for pfx in NON_TUNABLE_IPS:
        if ip.startswith(pfx):
            return False, f"IP {ip} is in non-tunable range ({pfx}*) — Akamai/non-tunable network", matched

    return True, f"{matched} CDN + IP {ip} is in tunable range", matched

def _tc_check_port(host, port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(3)
        r = s.connect_ex((host, port))
        s.close()
        return r == 0
    except:
        return False

def _tc_payload(domain, server):
    cf_payload = f"""CONNECT {domain}:443 HTTP/1.1
Host: {domain}
User-Agent: Mozilla/5.0
CF-Connecting-IP: 127.0.0.1
CF-IPCountry: US
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==
Sec-WebSocket-Version: 13"""

    generic = f"""CONNECT {domain}:443 HTTP/1.1
Host: {domain}
User-Agent: Mozilla/5.0
X-Forwarded-For: 127.0.0.1
Connection: keep-alive

# WebSocket:
GET / HTTP/1.1
Host: {domain}
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==
Sec-WebSocket-Version: 13"""

    if "cloudflare" in server.lower():
        return cf_payload
    return generic

def tunable_checker():
    clr(); banner()
    feature_header("⚡", "TUNABLE CHECKER",
                   "Check if SNI/domain is tunable for SSH tunneling",
                   OTHER_FEATURES)

    if not is_online():
        print(f"  {R}✘  No internet connection!{RST}")
        return pause()

    domain = input(f"  {W}Enter domain/SNI: {RST}").strip()
    if not domain:
        print(f"  {R}✘  No domain provided!{RST}")
        return pause()

    print(f"\n  {Y}Analyzing: {domain}{RST}\n")
    sep(C)

    # Step 1: Resolve IP
    sys.stdout.write(f"  {DIM}[ 1/4 ] Resolving IP...{RST}\r")
    sys.stdout.flush()
    try:
        ip = socket.gethostbyname(domain)
        print(f"  {G}✔{RST}  IP Address    {DIM}│{RST}  {W}{ip}{RST}         ")
    except:
        print(f"  {R}✘  Could not resolve domain!{RST}")
        return pause()

    # Step 2: Detect server (3 methods)
    sys.stdout.write(f"  {DIM}[ 2/4 ] Detecting CDN/Server (3 methods)...{RST}\r")
    sys.stdout.flush()
    server, ip_det, tcp_det, url_det = _tc_detect_server(domain, ip)
    print(f"  {G}✔{RST}  Server        {DIM}│{RST}  {C}{server}{RST}         ")
    print(f"  {DIM}    IP-based  : {ip_det or 'N/A'}{RST}")
    print(f"  {DIM}    TCP/SNI   : {tcp_det or 'N/A'}{RST}")
    print(f"  {DIM}    HTTP hdr  : {url_det or 'N/A'}{RST}")

    # Step 3: Check ports
    sys.stdout.write(f"  {DIM}[ 3/4 ] Checking ports...{RST}\r")
    sys.stdout.flush()
    p443  = _tc_check_port(ip, 443)
    p8080 = _tc_check_port(ip, 8080)
    pstr443  = f"{G}✔ OPEN{RST}" if p443  else f"{R}✘ CLOSED{RST}"
    pstr8080 = f"{G}✔ OPEN{RST}" if p8080 else f"{R}✘ CLOSED{RST}"
    print(f"  {G}✔{RST}  Port 443      {DIM}│{RST}  {pstr443}")
    print(f"  {G}✔{RST}  Port 8080     {DIM}│{RST}  {pstr8080}")

    # Step 4: Tunable verdict
    sys.stdout.write(f"  {DIM}[ 4/4 ] Checking tunability...{RST}\r")
    sys.stdout.flush()
    tunable, reason, matched = _tc_is_tunable(ip, server)
    sep(C)

    if tunable:
        print(f"\n  {GR2}{BLD}╔══════════════════════════════════╗{RST}")
        print(f"  {GR2}{BLD}║   ✔   STATUS : TUNABLE   ✔       ║{RST}")
        print(f"  {GR2}{BLD}╚══════════════════════════════════╝{RST}")
        print(f"\n  {G}✔{RST}  {reason}")
    else:
        print(f"\n  {R}{BLD}╔══════════════════════════════════╗{RST}")
        print(f"  {R}{BLD}║   ✘  STATUS : NON-TUNABLE  ✘     ║{RST}")
        print(f"  {R}{BLD}╚══════════════════════════════════╝{RST}")
        print(f"\n  {R}✘{RST}  {reason}")

    # Step 5: Payload if tunable
    if tunable:
        print(f"\n  {Y}{BLD}━━ SSH PAYLOAD ━━{RST}")
        sep(Y)
        for line in _tc_payload(domain, matched).split("\n"):
            print(f"  {C}{line}{RST}")
        sep(Y)
        print(f"\n  {W}Ports to try:{RST} 443, 8080, 2053, 2083, 2087, 2096")
        print(f"  {DIM}curl -x http://{domain}:443 https://api.ipify.org{RST}")

    # Save result
    try:
        dl = os.path.expanduser("~/storage/downloads")
        folder = dl if os.path.isdir(dl) else os.path.expanduser("~")
        out_path = os.path.join(folder, "tunable_results.txt")
        with open(out_path, "a") as f:
            f.write(f"{domain} | {ip} | {server} | "
                    f"{'TUNABLE' if tunable else 'NON-TUNABLE'} | {reason}\n")
        print(f"\n  {G}✔{RST}  Saved → {out_path}")
    except: pass

    sep(C); pause()

# ================================================================
#  MAIN
# ================================================================
ACTIONS = {
    "1":domain_scanner,"2":port_scanner,"3":http_info,
    "4":sni_scanner,"5":subdomain_finder,"6":extract_domains,
    "7":export_json,"8":ip_calculator,"9":local_network_scan,
    "10":device_info,"11":tunable_checker,"u":update_tool,
}

def main():
    startup_animation()   # ParaFast-style intro — runs only once at launch
    while True:
        try:
            ch = menu()
            if ch == "0":
                clr()
                clr()
                print()
                for i,ln in enumerate(DEV_ART):
                    print(f"  {BLD}{DEV_COLORS[i]}{ln}{RST}")
                print()
                for i,ln in enumerate(TREX_ART):
                    print(f"  {BLD}{TREX_COLORS[i]}{ln}{RST}")
                print()
                msg = "  Thanks for using our tool!  See you next time!"
                sys.stdout.write(f"  {DIM}")
                for ch2 in msg:
                    sys.stdout.write(ch2); sys.stdout.flush(); time.sleep(0.02)
                sys.stdout.write(RST+"\n\n")
                time.sleep(0.3)
                break
            elif ch in ACTIONS:
                try:
                    ACTIONS[ch]()
                except KeyboardInterrupt:
                    print(f"\n\n  {Y}⚠  Stopped. Menu pe wapis...{RST}")
                    time.sleep(0.6)
            elif ch == "":
                pass
            else:
                print(f"\n  {R}  Invalid! 0-10 ya U daalo.{RST}")
                time.sleep(0.6)
        except KeyboardInterrupt:
            print(f"\n  {Y}  Ctrl+C — Exit ke liye 0 daalo.{RST}")
            time.sleep(0.6)

if __name__ == "__main__":
    main()
