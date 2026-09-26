# 🛡️ MyArmor Browser

MyArmor Browser is a simple security-focused desktop browser built with Python, PyQt6, Flask, and Selenium.

It includes a custom login system, URL interception, webpage screenshot scanning, download protection, and a dark-themed browser interface.

## Features

- 🔐 Login system
- 🌐 Web browsing using Qt WebEngine
- 🛡️ URL interception
- 👀 Webpage screenshot scanning
- ✅ Allow / Block navigation
- 📥 Download handling
- 🎙️ Camera, microphone, and location permission prompts
- 🔎 Multiple search engines
- 📑 Multiple browser tabs
- 🎨 Custom dark UI
- 💾 Persistent browser cookies and cache

## How It Works

The project has three main parts:

    MyArmor Browser
          |
          +---- Authentication Server :8000
          |
          +---- Scan Server :8888
                     |
                     +---- Selenium
                     |
                     +---- Headless Chrome

### 1. Browser

The main application is built with:

- Python
- PyQt6
- Qt WebEngine

It handles browsing, tabs, login, URL interception, downloads, and permissions.

### 2. Authentication Server

The authentication server runs on:

    http://127.0.0.1:8000

It handles the login verification used by the browser.

### 3. Scan Server

The scan server runs on:

    http://127.0.0.1:8888

It uses Flask and Selenium to open an intercepted webpage in headless Chrome and take a screenshot.

## Requirements

- Python 3.10+
- Google Chrome / Chromium
- PyQt6
- PyQt6-WebEngine
- Flask
- Selenium
- Requests

Install the required packages:

    pip install PyQt6 PyQt6-WebEngine Flask selenium requests

## Project Structure

    MyArmor/
    │
    ├── browser.py
    ├── auth_server.py
    ├── scan_server.py
    ├── requirements.txt
    ├── README.md
    └── .gitignore

## Running

Open three terminals.

### Terminal 1 — Authentication Server

    python auth_server.py

### Terminal 2 — Scan Server

    python scan_server.py

### Terminal 3 — Browser

    python browser.py

Then the MyArmor login screen will appear.

## Default Development Login

The current development version uses:

    Username: simhadri
    Password: password

> ⚠️ Do not use these credentials in a production application.

## Intercept Mode

Turn on:

    🛡️ Intercept: ON

When a website is opened, MyArmor sends the URL to the scan server.

The scan server:

1. Opens the URL using Selenium.
2. Uses headless Chrome.
3. Waits for the page to load.
4. Takes a screenshot.
5. Sends the screenshot back to MyArmor.
6. The user can choose ALLOW or BLOCK.

## Important

The screenshot system is not a real malware or phishing detector.

It only captures the webpage visually. It does not guarantee that a website is safe.

## Security Note

This project is currently intended for learning and development.

Before using it in a real security environment, improve:

- Authentication
- Password storage
- HTTPS
- URL validation
- Session management
- Rate limiting
- Threat detection
- Selenium isolation

Never commit real passwords, API keys, or other secrets to GitHub.

## .gitignore

Add the following to `.gitignore`:

    __pycache__/
    *.pyc
    venv/
    .venv/
    web_profile/
    scan_result.png
    .env
    *.log

## Future Plans

- Real phishing detection
- URL reputation checking
- Malware scanning
- Better authentication
- Scan history
- Security alerts
- Improved performance
- Windows executable
- Linux support

## License

This project is for educational and development purposes.
