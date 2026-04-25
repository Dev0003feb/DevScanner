#!/usr/bin/env python3
# ================================================================
#
#   —͟͞⛦⃕͜𝐃𝐄𝐕࿐  &  T-REX  — ULTRA SCANNER v2.0
#   Optimized For ALL Devices | Offline + Online Support
#   Public Tool — Users Compatible
#
# ================================================================

import socket, ssl, sys, os, json, time, threading, re
import ipaddress
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

# ── Colors ──────────────────────────────────────────────────────
R   = "\033[91m"
G   = "\033[92m"
Y   = "\033[93m"
B   = "\033[94m"
M   = "\033[95m"
C   = "\033[96m"
W   = "\033[97m"
DIM = "\033[2m"
BLD = "\033[1m"
RST = "\033[0m"

# ================================================================
#  DEVICE AUTO DETECTION
# ================================================================
def detect_device():
    try:
        import multiprocessing
        cores = multiprocessing.cpu_count()
    except:
        cores = 1
    try:
        with open("/proc/meminfo") as f:
            for line in f:
                if "MemTotal" in line:
                    ram_mb = int(line.split()[1]) // 1024
                    break
    except:
        ram_mb = 512

    if cores <= 2 or ram_mb < 1500:
        return "LOW",  10, 2.0
    elif cores <= 4 or ram_mb < 3500:
        return "MID",  30, 1.2
    else:
        return "HIGH", 50, 0.7

TIER, DEFAULT_THREADS, TIMEOUT = detect_device()

# ================================================================
#  INTERNET CHECK
# ================================================================
def is_online():
    try:
        socket.setdefaulttimeout(2)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(("8.8.8.8", 53))
        s.close()
        return True
    except:
        return False

# ================================================================
#  HELPERS
# ================================================================
def clr():
    os.system("clear")

def sep(c=DIM):
    print(f"{c}{'─'*50}{RST}")

def pause():
    input(f"\n{DIM}  [Please Type Enter To Continue]{RST}")

def progress(done, total, extra=""):
    if total == 0: return
    pct = int((done / total) * 28)
    bar = f"{G}{'█'*pct}{DIM}{'░'*(28-pct)}{RST}"
    sys.stdout.write(f"\r  [{bar}] {Y}{done}/{total}{RST} {extra}   ")
    sys.stdout.flush()

def safe_path(path):
    return os.path.expanduser(path.strip().strip("'\""))

def get_server_name(ip):
    known = {
        "172.65": "Cloudflare",
        "104.16": "Cloudflare",
        "104.21": "Cloudflare",
        "49.44":  "AkamaiGHost",
        "23.32":  "Akamai",
        "23.64":  "Akamai",
        "45.123": "BigIP",
        "35.190": "Google",
        "142.250":"Google",
        "13.107": "Microsoft",
        "52.":    "Amazon",
        "54.":    "Amazon",
    }
    for prefix, name in known.items():
        if ip.startswith(prefix):
            return name
    return "Unknown"

# ================================================================
#  THREAD SELECTOR
# ================================================================
def select_threads():
    default = DEFAULT_THREADS
    print(f"""
  {BLD}{W}━━ Thread Select ━━{RST}

  {G}[1]{RST} 10   threads   {DIM}(Low device){RST}
  {G}[2]{RST} 30   threads   {DIM}(Mid device){RST}
  {G}[3]{RST} 50   threads   {DIM}(High device){RST}
  {G}[4]{RST} 100  threads   {DIM}(Very High){RST}
  {G}[5]{RST} Custom         {DIM}(Apna number daalo){RST}
  {DIM}  Enter = Auto ({default} threads — {TIER}){RST}
""")
    ch = input(f"  {W}Choice: {RST}").strip()
    if ch == "":    return default
    elif ch == "1": return 10
    elif ch == "2": return 30
    elif ch == "3": return 50
    elif ch == "4": return 100
    elif ch == "5":
        try:
            n = int(input(f"  {W}Threads daalo: {RST}").strip())
            return max(1, min(n, 500))
        except:
            return default
    else:
        return default

# ================================================================
#  BANNER  — BIG STYLISH
# ================================================================
def banner():
    online  = is_online()
    tier_c  = G if TIER == "HIGH" else Y if TIER == "MID" else R
    net_c   = G if online else R
    net_s   = "ONLINE  ✔" if online else "OFFLINE ✘"

    print(f"""{RST}
{M}  ╔══════════════════════════════════════════════════╗{RST}
{M}  ║{RST}                                                  {M}║{RST}
{M}  ║{RST}  {BLD}{M} ██████╗ ███████╗██╗   ██╗{RST}                   {M}║{RST}
{M}  ║{RST}  {BLD}{M} ██╔══██╗██╔════╝██║   ██║{RST}                   {M}║{RST}
{M}  ║{RST}  {BLD}{C} ██║  ██║█████╗  ██║   ██║{RST}                   {M}║{RST}
{M}  ║{RST}  {BLD}{C} ██║  ██║██╔══╝  ╚██╗ ██╔╝{RST}                   {M}║{RST}
{M}  ║{RST}  {BLD}{B} ██████╔╝███████╗ ╚████╔╝ {RST}                   {M}║{RST}
{M}  ║{RST}  {BLD}{B} ╚═════╝ ╚══════╝  ╚═══╝  {RST}                   {M}║{RST}
{M}  ║{RST}                                                  {M}║{RST}
{M}  ║{RST}  {BLD}{Y}  ████████╗    ██████╗ ███████╗██╗  ██╗{RST}      {M}║{RST}
{M}  ║{RST}  {BLD}{Y}     ██╔══╝    ██╔══██╗██╔════╝╚██╗██╔╝{RST}      {M}║{RST}
{M}  ║{RST}  {BLD}{R}     ██║  ████╗██████╔╝█████╗   ╚███╔╝ {RST}      {M}║{RST}
{M}  ║{RST}  {BLD}{R}     ██║  ╚═══╝██╔══██╗██╔══╝   ██╔██╗ {RST}      {M}║{RST}
{M}  ║{RST}  {BLD}{M}     ██║       ██║  ██║███████╗██╔╝ ██╗{RST}      {M}║{RST}
{M}  ║{RST}  {BLD}{M}     ╚═╝       ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝{RST}     {M}║{RST}
{M}  ║{RST}                                                  {M}║{RST}
{M}  ║{RST}  {BLD}{C}     ─── —͟͞⛦⃕𝐃𝐄𝐕 𝐎𝐏࿐  ✦  T-REX ───{RST}       {M}║{RST}
{M}  ║{RST}  {DIM}       ULTRA SCANNER v2.0 | 50k+ Ready{RST}         {M}║{RST}
{M}  ╚══════════════════════════════════════════════════╝{RST}
  {tier_c}● {TIER} Device{RST}  {DIM}|{RST}  {net_c}● {net_s}{RST}  {DIM}| Threads: {DEFAULT_THREADS} | T/O: {TIMEOUT}s{RST}
""")

# ================================================================
#  MENU
# ================================================================
def menu():
    clr()
    banner()
    print(f"""  {BLD}{W}━━━━━━ MAIN MENU ━━━━━━{RST}

  {G}[1]{RST}  🌐  Domain Scanner         {DIM}(It's work without Data ✔){RST}
  {G}[2]{RST}  ⚡  TCP Port Scanner       {DIM}(Local/Net){RST}
  {G}[3]{RST}  🔍  HTTP Info              {DIM}(It's need Data to Use ✔){RST}
  {G}[4]{RST}  🔒  SNI Scanner            {Y}(Mobile Data must be On ✔){RST}
  {G}[5]{RST}  🔎  Subdomain Finder       {DIM}(Net chahiye){RST}
  {G}[6]{RST}  📄  Extract Domains        {Y}(Offline ✔){RST}
  {G}[7]{RST}  💾  Export JSON            {Y}(Offline ✔){RST}
  {G}[8]{RST}  🖥️   IP Calculator          {Y}(Offline ✔){RST}
  {G}[9]{RST}  📡  Local Network Scan     {Y}(WiFi ✔){RST}
  {G}[10]{RST} 📱  Device Info            {Y}(Offline ✔){RST}
  {R}[0]{RST}   ✖  Exit

{DIM}  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RST}""")
    return input(f"\n  {W}Select: {RST}").strip()

# ================================================================
#  SAVE HELPER
# ================================================================
def save_prompt(data, name="scan_result.json"):
    ch = input(f"\n  {W}Result save karein? (y/n): {RST}").strip().lower()
    if ch != "y": return
    path = input(f"  {W}Path (Enter = ~/{name}): {RST}").strip()
    if not path:
        path = os.path.expanduser(f"~/{name}")
    try:
        with open(safe_path(path), "w") as f:
            json.dump(data, f, indent=2)
        print(f"  {G}✔ Saved: {path}{RST}")
    except Exception as e:
        print(f"  {R}✘ Save failed: {e}{RST}")

# ================================================================
#  1. DOMAIN SCANNER
# ================================================================
def domain_scanner():
    clr(); banner()
    print(f"  {BLD}{C}🌐  DOMAIN SCANNER{RST}"); sep(C)

    if not is_online():
        print(f"\n  {R}✘ Internet nahi hai! Ye feature net chahta hai.{RST}")
        print(f"  {Y}  SNI Scanner bina net ke chalao — Option [4]{RST}")
        return pause()

    target = input(f"\n  {W}Domain/IP daalo: {RST}").strip()
    if not target: return
    results = {"target": target, "time": str(datetime.now())}
    print()

    # IP
    try:
        ip = socket.gethostbyname(target)
        results["ip"] = ip
        print(f"  {G}✔ IP Address   :{RST} {W}{ip}{RST}")
    except:
        print(f"  {R}✘ DNS Resolve Failed{RST}")
        ip = None

    if ip:
        try:
            rev = socket.gethostbyaddr(ip)[0]
            results["reverse_dns"] = rev
            print(f"  {G}✔ Reverse DNS  :{RST} {rev}")
        except:
            print(f"  {DIM}  Reverse DNS  : N/A{RST}")
        try:
            all_ips = list({x[4][0] for x in socket.getaddrinfo(target, None)})
            results["all_ips"] = all_ips
            print(f"  {G}✔ All IPs      :{RST} {', '.join(all_ips)}")
        except:
            pass

    # SSL
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_OPTIONAL
        conn = ctx.wrap_socket(
            socket.create_connection((target, 443), timeout=TIMEOUT),
            server_hostname=target)
        cert = conn.getpeercert()
        conn.close()
        cn  = dict(x[0] for x in cert.get("subject",[])).get("commonName","N/A")
        exp = cert.get("notAfter","N/A")
        org = dict(x[0] for x in cert.get("issuer",[])).get("organizationName","N/A")
        results["ssl"] = {"cn": cn, "expiry": exp, "issuer": org}
        print(f"  {G}✔ SSL CN       :{RST} {cn}")
        print(f"  {G}✔ SSL Expiry   :{RST} {exp}")
        print(f"  {G}✔ SSL Issuer   :{RST} {org}")
    except:
        print(f"  {DIM}  SSL          : Not available{RST}")

    # HTTP
    try:
        import urllib.request
        for scheme in ["https","http"]:
            try:
                req  = urllib.request.Request(
                    f"{scheme}://{target}",
                    headers={"User-Agent":"Mozilla/5.0"})
                resp = urllib.request.urlopen(req, timeout=TIMEOUT)
                results["http_status"] = resp.status
                results["http_url"]    = resp.url
                print(f"  {G}✔ HTTP Status  :{RST} {resp.status}")
                print(f"  {G}✔ Final URL    :{RST} {resp.url}")
                break
            except: continue
    except: pass

    sep()
    save_prompt(results)
    pause()

# ================================================================
#  2. TCP PORT SCANNER
# ================================================================
def scan_port(host, port, timeout):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        r = s.connect_ex((host, port))
        s.close()
        return port if r == 0 else None
    except:
        return None

def port_scanner():
    clr(); banner()
    print(f"  {BLD}{C}⚡  TCP PORT SCANNER{RST}"); sep(C)

    target = input(f"\n  {W}IP / Domain daalo: {RST}").strip()
    if not target: return

    print(f"""
  {W}Port Range:{RST}
  {G}[1]{RST} Common Ports (Top 30)
  {G}[2]{RST} Full Range   (1–1024)
  {G}[3]{RST} Custom Range
  {G}[4]{RST} Single Port
""")
    ch = input(f"  {W}Choice: {RST}").strip()

    COMMON = [21,22,23,25,53,80,110,111,135,139,143,
              443,445,993,995,1723,3306,3389,5900,
              8080,8443,8888,9090,27017,6379,5432,1521,1433,2181]

    if ch == "1":   ports = COMMON
    elif ch == "2": ports = list(range(1, 1025))
    elif ch == "3":
        try:
            r = input(f"  {W}Range (e.g. 1-500): {RST}").strip().split("-")
            ports = list(range(int(r[0]), int(r[1])+1))
        except:
            print(f"  {R}Invalid{RST}"); return pause()
    elif ch == "4":
        try: ports = [int(input(f"  {W}Port: {RST}").strip())]
        except: return pause()
    else: return

    threads = select_threads()

    try:
        ip = socket.gethostbyname(target)
    except:
        print(f"  {R}✘ DNS Failed{RST}"); return pause()

    print(f"\n  {Y}Scanning {ip} — {len(ports)} ports — {threads} threads...{RST}\n")
    open_ports = []
    done = 0
    lock = threading.Lock()

    def worker(port):
        nonlocal done
        result = scan_port(ip, port, TIMEOUT)
        with lock:
            done += 1
            if done % 3 == 0 or done == len(ports):
                progress(done, len(ports))
        return result

    with ThreadPoolExecutor(max_workers=threads) as ex:
        futures = {ex.submit(worker, p): p for p in ports}
        for f in as_completed(futures):
            r = f.result()
            if r: open_ports.append(r)

    print(); sep()

    SERVICES = {
        21:"FTP",22:"SSH",23:"Telnet",25:"SMTP",53:"DNS",
        80:"HTTP",110:"POP3",143:"IMAP",443:"HTTPS",445:"SMB",
        3306:"MySQL",3389:"RDP",5432:"PostgreSQL",6379:"Redis",
        8080:"HTTP-Alt",8443:"HTTPS-Alt",27017:"MongoDB",
        1433:"MSSQL",1521:"Oracle",8888:"HTTP-Alt",2181:"ZooKeeper"
    }

    if open_ports:
        open_ports.sort()
        print(f"\n  {G}{BLD}Open Ports: {len(open_ports)}{RST}\n")
        for p in open_ports:
            svc = SERVICES.get(p, "Unknown")
            print(f"  {G}✔{RST}  {Y}{p:<6}{RST}  {C}{svc}{RST}")
    else:
        print(f"\n  {R}No open ports found.{RST}")

    save_prompt({"target": target, "ip": ip, "open_ports": open_ports})
    pause()

# ================================================================
#  3. HTTP INFO
# ================================================================
def http_info():
    clr(); banner()
    print(f"  {BLD}{C}🔍  HTTP INFO{RST}"); sep(C)

    if not is_online():
        print(f"\n  {R}✘ Internet nahi hai!{RST}")
        return pause()

    target = input(f"\n  {W}Domain/URL daalo: {RST}").strip()
    if not target: return

    urls = [target] if target.startswith("http") else [f"https://{target}", f"http://{target}"]

    import urllib.request
    results = {}
    print()

    for url in urls:
        try:
            req  = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            resp = urllib.request.urlopen(req, timeout=TIMEOUT)
            hdrs = dict(resp.headers)
            results = {
                "url":          resp.url,
                "status":       resp.status,
                "server":       hdrs.get("server","N/A"),
                "content_type": hdrs.get("content-type","N/A"),
                "powered_by":   hdrs.get("x-powered-by","N/A"),
                "cdn":          hdrs.get("via", hdrs.get("x-cdn","N/A")),
                "cache":        hdrs.get("cache-control","N/A"),
                "hsts":         hdrs.get("strict-transport-security","N/A"),
                "all_headers":  hdrs
            }
            print(f"  {G}✔ URL          :{RST} {resp.url}")
            print(f"  {G}✔ Status       :{RST} {resp.status}")
            print(f"  {G}✔ Server       :{RST} {hdrs.get('server','N/A')}")
            print(f"  {G}✔ Content-Type :{RST} {hdrs.get('content-type','N/A')}")
            print(f"  {G}✔ Powered-By   :{RST} {hdrs.get('x-powered-by','N/A')}")
            print(f"  {G}✔ CDN/Via      :{RST} {hdrs.get('via', hdrs.get('x-cdn','N/A'))}")
            print(f"  {G}✔ Cache        :{RST} {hdrs.get('cache-control','N/A')}")
            print(f"  {G}✔ HSTS         :{RST} {hdrs.get('strict-transport-security','N/A')}")
            break
        except Exception as e:
            print(f"  {R}✘ {url} — {e}{RST}")

    sep()
    save_prompt(results)
    pause()

# ================================================================
#  4. SNI SCANNER  ✦ MAIN FEATURE — Bina Net ke Kaam Karta Hai
# ================================================================
def sni_connect(host, port, timeout=2.0):
    ip = "-"
    code = "-"
    server = "Unknown"

    try:
        ip = socket.gethostbyname(host)
        server = get_server_name(ip)
    except:
        ip = "-"

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        s.connect((ip if ip != "-" else host, port))

        if port == 443:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            ss = ctx.wrap_socket(s, server_hostname=host)
            req = (f"HEAD / HTTP/1.1\r\nHost: {host}\r\n"
                   f"User-Agent: Mozilla/5.0\r\nConnection: close\r\n\r\n")
            ss.sendall(req.encode())
            resp = ss.recv(512).decode("utf-8", errors="ignore")
            ss.close()
        else:
            req = (f"HEAD / HTTP/1.1\r\nHost: {host}\r\n"
                   f"User-Agent: Mozilla/5.0\r\nConnection: close\r\n\r\n")
            s.sendall(req.encode())
            resp = s.recv(512).decode("utf-8", errors="ignore")
            s.close()

        match = re.search(r"HTTP/[\d.]+ (\d+)", resp)
        if match:
            code = match.group(1)

        srv_m = re.search(r"[Ss]erver: ([^\r\n]+)", resp)
        if srv_m:
            server = srv_m.group(1).strip()[:14]

        return code, ip, server

    except ssl.SSLError:
        return "SSL", ip, server
    except socket.timeout:
        return "TMO", ip, server
    except ConnectionRefusedError:
        return "REF", ip, server
    except:
        return "-", ip, server

def sni_scanner():
    clr(); banner()
    print(f"  {BLD}{C}🔒  SNI SCANNER{RST}  {Y}(Bina Net ke bhi kaam karta hai ✔){RST}")
    sep(C)

    print(f"""
  {W}Subdomains file ka path daalo:{RST}
  {DIM}  e.g: /storage/emulated/0/Download/myfile_subdomains.txt{RST}
""")
    in_path = safe_path(input(f"  {W}File path: {RST}").strip())

    if not os.path.exists(in_path):
        print(f"\n  {R}✘ File nahi mili: {in_path}{RST}")
        return pause()

    # Read & clean domains
    with open(in_path, "r", errors="ignore") as f:
        raw = [l.strip() for l in f if l.strip() and not l.startswith("#")]

    domains = []
    for d in raw:
        d = re.sub(r"https?://", "", d).split("/")[0].split(":")[0].strip()
        if d and "." in d:
            domains.append(d)
    domains = list(dict.fromkeys(domains))

    if not domains:
        print(f"\n  {R}✘ File mein koi valid domain nahi mila.{RST}")
        return pause()

    # Output file
    folder   = os.path.dirname(in_path)
    base     = os.path.basename(in_path)
    out_path = os.path.join(folder, f"sni_{base}")

    PORTS = [80, 443]  # ✦ Only 80 & 443

    print(f"\n  {G}✔ Domains loaded :{RST} {len(domains)}")
    print(f"  {G}✔ Ports          :{RST} {', '.join(map(str, PORTS))}")
    print(f"  {G}✔ Output file    :{RST} {out_path}")

    threads = select_threads()

    total = len(domains) * len(PORTS)
    print(f"\n  {Y}Scanning suru — {len(domains)} domains × {len(PORTS)} ports = {total} checks...{RST}\n")
    sep()

    # Table header
    hdr = f"{'Code':<6}| {'IP':<16}| {'Server':<15}| Host"
    print(f"  {BLD}{W}{hdr}{RST}")
    sep()

    done    = 0
    results = []
    lock    = threading.Lock()

    out_f = open(out_path, "w", buffering=1, encoding="utf-8")
    out_f.write(f"# —͟͞⛦⃕͜᪾ 𝐃𝐄𝐕࿐ & T-REX — SNI SCAN\n")
    out_f.write(f"# Date   : {datetime.now()}\n")
    out_f.write(f"# Source : {in_path}\n")
    out_f.write(f"# Ports  : {PORTS}\n")
    out_f.write(f"# Threads: {threads}\n\n")
    out_f.write(f"{'Code':<6}| {'IP':<16}| {'Server':<15}| Host\n")
    out_f.write("─" * 60 + "\n")

    def worker(domain, port):
        nonlocal done
        code, ip, server = sni_connect(domain, port, TIMEOUT)
        host_str = f"{domain}:{port}"
        row = {"code": str(code), "ip": ip, "server": server, "host": host_str}

        with lock:
            done += 1

            # Color based on response code
            if str(code) in ["200","301","302","307","308"]:
                cc = G
            elif str(code) in ["400","401","403","404","500","502","503"]:
                cc = Y
            elif str(code) in ["TMO","-"]:
                cc = DIM
            else:
                cc = W

            line = f"{str(code):<6}| {str(ip):<16}| {str(server):<15}| {host_str}"

            # Print to screen (skip timeouts for clean output)
            if str(code) not in ["TMO", "-"]:
                print(f"  {cc}{line}{RST}")

            # Write all to file
            out_f.write(line + "\n")
            out_f.flush()
            results.append(row)

            # Live progress bar at bottom
            if done % 5 == 0 or done == total:
                pct = int((done / total) * 25)
                bar = f"{'█'*pct}{'░'*(25-pct)}"
                sys.stdout.write(
                    f"\r  {DIM}SCANNING [{bar}] {done}/{total}  {RST}   "
                )
                sys.stdout.flush()

    with ThreadPoolExecutor(max_workers=threads) as ex:
        futures = []
        for domain in domains:
            for port in PORTS:
                futures.append(ex.submit(worker, domain, port))
        for f in as_completed(futures):
            pass

    out_f.write(f"\n# ─────────────────────────────────────\n")
    out_f.write(f"# Total Scanned: {len(results)}\n")
    out_f.write(f"# Responsive   : {len([r for r in results if r['code'] not in ['-','TMO','REF']])}\n")
    out_f.write(f"# Done         : {datetime.now()}\n")
    out_f.close()

    print()
    sep()
    ok = [r for r in results if r["code"] not in ["-","TMO","REF","SSL"]]
    print(f"\n  {G}{BLD}✔ Scan Complete!{RST}")
    print(f"  {G}✔ Total scanned  :{RST} {len(results)}")
    print(f"  {G}✔ Responsive     :{RST} {len(ok)}")
    print(f"  {G}✔ Saved to       :{RST} {out_path}")
    pause()

# ================================================================
#  5. SUBDOMAIN FINDER
# ================================================================
WORDLIST = [
    "www","mail","ftp","smtp","pop","imap","webmail","cpanel","admin","api",
    "app","dev","test","staging","beta","demo","cdn","static","assets","media",
    "img","images","blog","shop","store","portal","dashboard","panel","auth",
    "login","register","account","user","users","support","help","docs","wiki",
    "status","monitor","metrics","vpn","remote","ssh","files","download","upload",
    "storage","backup","db","database","mysql","mongo","redis","search","cache",
    "proxy","gateway","ns1","ns2","mx","mx1","mx2","smtp1","smtp2","autodiscover",
    "autoconfig","calendar","video","stream","live","news","feed","rss","security",
    "ssl","owa","exchange","cloud","internal","intranet","corp","office","aws",
    "azure","k8s","docker","ci","cd","build","deploy","staging2","uat","qa",
    "pre","prod","sandbox","lab","data","analytics","report","stats","log","audit",
    "legal","careers","partner","client","customer","service","server","node","lb",
    "ha","dr","archive","old","legacy","v1","v2","v3","new","next","alpha","preview",
    "edge","origin","primary","secondary","master","read","write","public","private",
    "secure","sso","oauth","ldap","dns","ntp","vault","manager","management",
    "control","admin2","root","sys","network","relay","mta","spam","filter",
    "firewall","ids","waf","api2","api3","apiv1","apiv2","rest","graphql","ws",
    "mobile","m","pwa","amp","fast","speed","turbo","global","local","geo","maps",
    "tracking","iot","device","health","healthcheck","ping","uptime","maintenance",
    "forum","community","feedback","forms","crm","erp","billing","payment","checkout",
    "order","fleet","telemetry","debug","profile","info","test2","mock","sample",
]

def subdomain_finder():
    clr(); banner()
    print(f"  {BLD}{C}🔎  SUBDOMAIN FINDER{RST}"); sep(C)

    if not is_online():
        print(f"\n  {R}✘ Internet nahi hai! Subdomain resolve ke liye net chahiye.{RST}")
        print(f"  {Y}  Agar subdomains already hain toh SNI Scanner chalao — [4]{RST}")
        return pause()

    print(f"""
  {W}Domains file ka path daalo:{RST}
  {DIM}  e.g: /storage/emulated/0/Download/domains.txt{RST}
""")
    in_path = safe_path(input(f"  {W}File path: {RST}").strip())

    if not os.path.exists(in_path):
        print(f"\n  {R}✘ File nahi mili: {in_path}{RST}")
        return pause()

    with open(in_path, "r", errors="ignore") as f:
        base_domains = list(dict.fromkeys([
            re.sub(r"https?://","",l.strip()).split("/")[0].strip()
            for l in f if l.strip() and not l.startswith("#") and "." in l
        ]))

    if not base_domains:
        print(f"\n  {R}✘ Koi valid domain nahi mila.{RST}")
        return pause()

    folder   = os.path.dirname(in_path)
    base_n   = os.path.splitext(os.path.basename(in_path))[0]
    out_path = os.path.join(folder, f"{base_n}_subdomains.txt")

    threads    = select_threads()
    total_work = len(base_domains) * len(WORDLIST)

    print(f"\n  {G}✔ Base domains   :{RST} {len(base_domains)}")
    print(f"  {G}✔ Wordlist size  :{RST} {len(WORDLIST)}")
    print(f"  {G}✔ Total checks   :{RST} {total_work}")
    print(f"  {G}✔ Output file    :{RST} {out_path}")
    print(f"\n  {Y}Scanning...{RST}\n")

    found = []
    done  = 0
    lock  = threading.Lock()
    out_f = open(out_path, "w", buffering=1, encoding="utf-8")
    out_f.write(f"# —͟͞⛦⃕͜᪾ 𝐃𝐄𝐕࿐ & T-REX — Subdomains\n")
    out_f.write(f"# Source: {in_path}\n# Date: {datetime.now()}\n\n")

    def check(base, prefix):
        nonlocal done
        sub = f"{prefix}.{base}"
        try:
            socket.setdefaulttimeout(TIMEOUT)
            ip = socket.gethostbyname(sub)
            with lock:
                done += 1
                found.append(sub)
                print(f"  {G}✔{RST} {sub:<45} {DIM}{ip}{RST}")
                out_f.write(sub + "\n")
                out_f.flush()
        except:
            with lock:
                done += 1
                if done % 25 == 0:
                    progress(done, total_work, f"{G}{len(found)} found{RST}")

    with ThreadPoolExecutor(max_workers=threads) as ex:
        futures = [ex.submit(check, b, p) for b in base_domains for p in WORDLIST]
        for f in as_completed(futures): pass

    out_f.write(f"\n# Total: {len(found)}\n")
    out_f.close()

    print(); sep()
    print(f"\n  {G}{BLD}✔ Done!{RST}")
    print(f"  {G}✔ Subdomains found :{RST} {len(found)}")
    print(f"  {G}✔ Saved to         :{RST} {out_path}")
    print(f"\n  {Y}Ab SNI Scanner chalao (Option 4){RST}")
    print(f"  {Y}File: {out_path}{RST}")
    pause()

# ================================================================
#  6. EXTRACT DOMAINS  (Offline)
# ================================================================
def extract_domains():
    clr(); banner()
    print(f"  {BLD}{C}📄  EXTRACT DOMAINS  {Y}(Offline ✔){RST}"); sep(C)

    print(f"""
  {W}Kisi bhi file ka path daalo:{RST}
  {DIM}  (HTML, text, mixed — sab domains extract ho jayenge){RST}
""")
    in_path = safe_path(input(f"  {W}File path: {RST}").strip())

    if not os.path.exists(in_path):
        print(f"\n  {R}✘ File nahi mili{RST}"); return pause()

    with open(in_path, "r", errors="ignore") as f:
        content = f.read()

    pattern = r"(?:https?://)?(?:www\.)?([a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z]{2,})+)"
    domains = sorted(set(re.findall(pattern, content)))

    if not domains:
        print(f"\n  {R}✘ Koi domain nahi mila.{RST}"); return pause()

    folder   = os.path.dirname(in_path)
    out_path = os.path.join(folder, "extracted_domains.txt")

    with open(out_path, "w") as f:
        f.write(f"# —͟͞⛦⃕͜᪾ 𝐃𝐄𝐕࿐ & T-REX — Extracted Domains\n")
        f.write(f"# Source: {in_path}\n# Date: {datetime.now()}\n\n")
        for d in domains:
            f.write(d + "\n")

    print(f"\n  {G}{BLD}✔ Extracted: {len(domains)} domains{RST}")
    print(f"  {G}✔ Saved to : {out_path}{RST}")
    print(f"\n  {DIM}Pehle 10:{RST}")
    for d in domains[:10]:
        print(f"  {C}{d}{RST}")
    if len(domains) > 10:
        print(f"  {DIM}  ...aur {len(domains)-10} aur{RST}")
    pause()

# ================================================================
#  7. EXPORT JSON  (Offline)
# ================================================================
def export_json():
    clr(); banner()
    print(f"  {BLD}{C}💾  EXPORT JSON  {Y}(Offline ✔){RST}"); sep(C)

    print(f"""
  {W}.txt file ko JSON mein convert karo:{RST}
  {DIM}  (Ek line = ek entry){RST}
""")
    in_path = safe_path(input(f"  {W}Input .txt file: {RST}").strip())

    if not os.path.exists(in_path):
        print(f"\n  {R}✘ File nahi mili{RST}"); return pause()

    with open(in_path, "r", errors="ignore") as f:
        lines = [l.strip() for l in f if l.strip() and not l.startswith("#")]

    data = {
        "tool":     "—͟͞⛦⃕͜᪾ 𝐃𝐄𝐕࿐ & T-REX Ultra Scanner",
        "source":   in_path,
        "exported": str(datetime.now()),
        "total":    len(lines),
        "entries":  lines
    }

    folder   = os.path.dirname(in_path)
    base     = os.path.splitext(os.path.basename(in_path))[0]
    out_path = os.path.join(folder, f"{base}.json")

    with open(out_path, "w") as f:
        json.dump(data, f, indent=2)

    print(f"\n  {G}✔ Total entries : {len(lines)}{RST}")
    print(f"  {G}✔ Saved to      : {out_path}{RST}")
    pause()

# ================================================================
#  8. IP CALCULATOR  (Offline)
# ================================================================
def ip_calculator():
    clr(); banner()
    print(f"  {BLD}{C}🖥️   IP CALCULATOR  {Y}(Offline ✔){RST}"); sep(C)

    inp = input(f"\n  {W}IP/CIDR daalo (e.g. 192.168.1.0/24): {RST}").strip()
    if not inp: return

    try:
        net = ipaddress.ip_network(inp, strict=False)
        print(f"""
  {G}✔ Network    :{RST} {net.network_address}
  {G}✔ Broadcast  :{RST} {net.broadcast_address}
  {G}✔ Netmask    :{RST} {net.netmask}
  {G}✔ Hostmask   :{RST} {net.hostmask}
  {G}✔ Prefix     :{RST} /{net.prefixlen}
  {G}✔ Total IPs  :{RST} {net.num_addresses}
  {G}✔ Usable IPs :{RST} {max(0, net.num_addresses - 2)}
  {G}✔ Version    :{RST} IPv{net.version}
  {G}✔ Private    :{RST} {net.is_private}""")
        hosts = list(net.hosts())
        if hosts:
            print(f"\n  {DIM}Host range:{RST}")
            print(f"  {C}{hosts[0]}  —  {hosts[-1]}{RST}")
    except Exception as e:
        print(f"\n  {R}✘ Invalid: {e}{RST}")
    pause()

# ================================================================
#  9. LOCAL NETWORK SCAN  (WiFi — no data needed)
# ================================================================
def local_network_scan():
    clr(); banner()
    print(f"  {BLD}{C}📡  LOCAL NETWORK SCAN  {Y}(WiFi ✔){RST}"); sep(C)

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
    except:
        local_ip = "192.168.1.100"

    net_base = ".".join(local_ip.split(".")[:3])
    print(f"\n  {G}✔ Your IP    :{RST} {local_ip}")
    print(f"  {G}✔ Scanning   :{RST} {net_base}.1 — {net_base}.254")

    threads = select_threads()
    print(f"\n  {Y}Scanning...{RST}\n")

    found = []
    done  = 0
    lock  = threading.Lock()

    def ping_host(i):
        nonlocal done
        ip = f"{net_base}.{i}"
        alive = False
        for port in [80, 443, 22, 8080]:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(0.5)
                if s.connect_ex((ip, port)) == 0:
                    alive = True
                    s.close()
                    break
                s.close()
            except:
                pass
        if alive:
            try: hostname = socket.gethostbyaddr(ip)[0]
            except: hostname = "Unknown"
            with lock:
                done += 1
                found.append({"ip": ip, "hostname": hostname})
                print(f"  {G}✔{RST} {ip:<18} {C}{hostname}{RST}")
        else:
            with lock:
                done += 1
                if done % 10 == 0:
                    progress(done, 254)

    with ThreadPoolExecutor(max_workers=threads) as ex:
        futures = [ex.submit(ping_host, i) for i in range(1, 255)]
        for f in as_completed(futures): pass

    print(); sep()
    print(f"\n  {G}{BLD}Devices found: {len(found)}{RST}")
    save_prompt({"network": f"{net_base}.0/24", "devices": found}, "local_scan.json")
    pause()

# ================================================================
#  10. DEVICE INFO  (Offline)
# ================================================================
def device_info():
    clr(); banner()
    print(f"  {BLD}{C}📱  DEVICE INFO  {Y}(Offline ✔){RST}"); sep(C)

    import platform
    print(f"""
  {G}✔ OS           :{RST} {platform.system()} {platform.release()}
  {G}✔ Architecture :{RST} {platform.machine()}
  {G}✔ Python       :{RST} {platform.python_version()}
  {G}✔ Device Tier  :{RST} {TIER}
  {G}✔ Def.Threads  :{RST} {DEFAULT_THREADS}
  {G}✔ Timeout      :{RST} {TIMEOUT}s""")

    try:
        ram_total = avail = 0
        with open("/proc/meminfo") as f:
            for line in f:
                if "MemTotal" in line:
                    ram_total = int(line.split()[1]) // 1024
                if "MemAvailable" in line:
                    avail = int(line.split()[1]) // 1024
        print(f"  {G}✔ RAM Total    :{RST} {ram_total} MB")
        print(f"  {G}✔ RAM Free     :{RST} {avail} MB")
    except: pass

    try:
        import multiprocessing
        print(f"  {G}✔ CPU Cores    :{RST} {multiprocessing.cpu_count()}")
    except: pass

    try:
        with open("/proc/cpuinfo") as f:
            for line in f:
                if "Hardware" in line:
                    print(f"  {G}✔ Hardware     :{RST} {line.split(':')[1].strip()}")
                    break
    except: pass

    try:
        import subprocess
        r = subprocess.run(["ip","addr"], capture_output=True, text=True, timeout=2)
        ips = re.findall(r"inet (\d+\.\d+\.\d+\.\d+)", r.stdout)
        if ips: print(f"  {G}✔ Local IPs    :{RST} {', '.join(ips)}")
    except: pass

    pause()

# ================================================================
#  MAIN LOOP
# ================================================================
def main():
    ACTIONS = {
        "1":  domain_scanner,
        "2":  port_scanner,
        "3":  http_info,
        "4":  sni_scanner,
        "5":  subdomain_finder,
        "6":  extract_domains,
        "7":  export_json,
        "8":  ip_calculator,
        "9":  local_network_scan,
        "10": device_info,
    }

    while True:
        choice = menu()
        if choice == "0":
            clr()
            print(f"""
{M}  ╔══════════════════════════════════════╗
  ║                                      ║
  ║   —͟͞⛦⃕͜᪾  𝐃𝐄𝐕࿐   ✦   T-REX         ║
  ║      Thanks for using our tool!      ║
  ║         See you next time 👋         ║
  ║                                      ║
  ╚══════════════════════════════════════╝{RST}
""")
            break
        elif choice in ACTIONS:
            ACTIONS[choice]()
        else:
            print(f"\n  {R}  Invalid choice! Dobara try karo.{RST}")
            time.sleep(0.8)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n  {Y}  Ctrl+C — Tool band ho gaya. Bye! 👋{RST}\n")
        sys.exit(0)
