# 🔐 Basic Auth Brute-Forcer

A powerful, multiprocessing-based **Basic Authentication brute-force** tool written in Python. This tool is built for **authorized penetration testing**, offering advanced features such as proxy support, timeout handling, and a live progress bar for better visibility.

---

## 🚀 Features

✅ Multiprocessing support (fast parallel login attempts)  
✅ Live animated progress bar  
✅ Efficient handling of large username/password files (loaded once)  
✅ Retry + backoff for network errors  
✅ Supports proxy (HTTP/SOCKS)  
✅ Optional skipping of non-latin1 credentials (`--allow-nonlatin`)  
✅ Auto-corrects to HTTPS if HTTP is passed  
✅ Stops as soon as valid credentials are found  

---

## 📦 Installation

```bash
git clone https://github.com/HoumanPashaei/BasicAuthBruteForcer
cd BasicAuthBruteForcer
pip install -r requirements.txt
```

> **Python 3.7+ is required**

---

## 📚 Usage

```bash
python BruteForce.py -d https://target.com/protected -u admin -P passwords.txt -w 4 -x http://127.0.0.1:8080
```

### 🔧 Options

| Option                 | Description                                                 |
|------------------------|-------------------------------------------------------------|
| `-d`, `--domain`        | Target URL (HTTPS or HTTP)                                  |
| `-u`, `--username`      | Single username to test                                     |
| `-U`, `--userfile`      | File containing a list of usernames                         |
| `-P`, `--passfile`      | File containing a list of passwords (required)              |
| `-x`, `--proxy`         | Proxy URL (`http://` or `socks5://`)                        |
| `-w`, `--workers`       | Number of parallel processes (default: all CPUs)            |
| `--allow-nonlatin`      | **Include** non-latin1 credentials (instead of skipping)    |

---

## 🔄 Examples

### Single Username + Password File
```bash
python BruteForce.py -d https://example.com/auth -u admin -P passwords.txt
```

### Multiple Usernames + Password File
```bash
python BruteForce.py -d https://example.com/auth -U users.txt -P passwords.txt
```

### Use Proxy (e.g., Burp or TOR)
```bash
python BruteForce.py -d https://example.com/auth -u admin -P passwords.txt -x http://127.0.0.1:8080
```

### High-Speed Attack with 8 Workers
```bash
python BruteForce.py -d https://example.com/auth -U users.txt -P passwords.txt -w 8
```

### Include Non-Latin1 Credentials
```bash
python BruteForce.py -d https://example.com/auth -U users.txt -P passwords.txt --allow-nonlatin
```

---

## 🧠 How It Works

- Loads the username and password lists **once** for optimal performance.
- Uses `multiprocessing.Pool` to run login attempts in parallel.
- For each attempt, a `requests` session is created with retry + timeout handling.
- If a credential works (HTTP 200), the attack stops immediately.
- By default, skips credentials that are not compatible with `latin1`; use `--allow-nonlatin` to keep them.
- Progress is printed in a dynamic bar like:
  ```
  [+] Progress: [■■■■■■□□□□□□] 52.5% (105/200)
  ```

---

## ✅ Requirements

- Python 3.7+
- `requests`
- `colorama`

Install manually if needed:
```bash
pip install requests colorama
```

---

## 📁 File Structure

```
BruteForce.py      # Main script
requirements.txt
README.md          # You're here
```

---

