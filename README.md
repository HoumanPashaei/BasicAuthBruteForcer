# 🔐 Basic Auth Brute-Forcer

A powerful, multiprocessing-based **Basic Authentication brute-force** tool written in Python. This tool is built for **authorized penetration testing**, offering advanced features such as proxy support, timeout handling, and a live progress bar for better visibility.

---

## 🚀 Features

✅ Multiprocessing support (fast parallel login attempts)  
✅ Live animated progress bar  
✅ Handles large username/password files safely  
✅ Retry + backoff for network errors  
✅ Supports proxy (HTTP/SOCKS)  
✅ Skips invalid (non-latin1) credentials silently  
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
python bruteforce.py -d https://target.com/protected -u admin -P passwords.txt -t 4
```

### 🔧 Options

| Option             | Description                                       |
|--------------------|---------------------------------------------------|
| `-d`, `--domain`    | Target URL (HTTPS required)                      |
| `-u`, `--username`  | Single username to test                          |
| `-U`, `--userfile`  | File containing a list of usernames              |
| `-P`, `--passfile`  | File containing a list of passwords (required)   |
| `-x`, `--proxy`     | Proxy URL (`http://` or `socks5://`)             |
| `-t`, `--threads`   | Number of parallel processes (default: all CPUs) |

---

## 🔄 Examples

### Single Username + Password File
```bash
python bruteforce.py -d https://example.com/auth -u admin -P passwords.txt
```

### Multiple Usernames + Password File
```bash
python bruteforce.py -d https://example.com/auth -U users.txt -P passwords.txt
```

### Use Proxy (e.g., Burp or TOR)
```bash
python bruteforce.py -d https://example.com/auth -u admin -P passwords.txt -x http://127.0.0.1:8080
```

### High-Speed Attack with 8 Workers
```bash
python bruteforce.py -d https://example.com/auth -U users.txt -P passwords.txt -t 8
```

---

## 🧠 How It Works

- Uses `multiprocessing.Pool` to run login attempts in parallel.
- For each attempt, a `requests` session is created with retry + timeout handling.
- If a credential works (HTTP 200), the attack stops immediately.
- Invalid credentials (non-latin1) are ignored silently to avoid crashing.
- Progress is printed in a dynamic bar like:
  ```
  [+] Progress: [■■■■■■□□□□□□] 52.5% (105/200)
  ```

---

## ✅ Requirements

- Python 3.7+
- `requests`
- No third-party dependencies other than Python standard libs

Install manually if needed:
```bash
pip install requests
```

---

## 📁 File Structure

```
bruteforce.py      # Main script
users.txt          # (example usernames)
passwords.txt      # (example passwords)
README.md          # You're here
```

---

## ❤️ Contributions

Pull requests are welcome! Feel free to fork and improve this script.

---

## 📜 License

This project is licensed under the [MIT License](LICENSE).
