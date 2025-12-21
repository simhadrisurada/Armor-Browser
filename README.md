# 🛡️ Armor: Safe Browsing Browser

**Armor** is a security-first web browser that allows access **only to verified, trusted websites**, protecting users from DDoS, XSS, Phishing, and IDOR attacks.  
Instead of reacting to attacks, Armor **prevents unsafe access before it happens**.  

---

## 🖥️ Requirements & Setup

### 📦 System Requirements
- Python 3.8 or higher  
- Supported OS: Windows, Linux, macOS  
- Internet connection (for website verification)  

### 🖼️ Required Assets
Make sure the following files are in your project folder:  
- `background.png` → Browser background  
- `chrome.png` → Browser icon  

⚠️ Missing assets may break the UI.

### 📚 Python Dependencies
Armor uses **WebView** to render web content securely:

```bash
pip install pywebview
```
```bash
armor-safe-browsing/
│
├── main.py
├── background.png
├── chrome.png
├── README.md
└── requirements.txt
```
---
## 🔑 Key Features

- Secure-Only Browsing: Access only verified domains. Unsafe sites never load.

- Safe Search Engine: Autocomplete suggestions from trusted websites only.

- Service-Based Safe Alternatives: Blocked sites suggest verified alternatives.

- Browser-Dependent Websites: API keys required, prevents scraping/cloning.

- UID-Based User Access: Each user gets a unique ID for secure sessions.

- Hidden URLs & API Paths: Users see only main domains, preventing IDOR attacks.

- Client-Side Protection: Dev tools disabled, script rewriting blocked, redirect abuse prevented.

