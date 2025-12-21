🛡️ Armor: Safe Browsing

Armor is a security-first web browser designed to allow access only to verified, trusted websites, protecting users from common web attacks such as DDoS, Cross-Site Scripting (XSS), Phishing, and IDOR.
Instead of securing users after an attack, Armor prevents unsafe access before it happens.

🧰 Requirements & Setup
📦 System Requirements

Python 3.8 or higher

Supported OS: Windows / Linux / macOS

Internet connection (for website verification)

🖼️ Required Assets

Make sure the following files are present in the project directory:

background.png → Background image for the browser UI

chrome.png → Browser icon / branding image

⚠️ The application UI will not render correctly if these assets are missing.

📚 Python Dependencies

Armor uses WebView to securely render web content inside the application.

Install the required module using:

pip install pywebview


(Optional but recommended: use a virtual environment.)

▶️ Running the Application

From the project root directory, run:

python main.py


Replace main.py with your actual entry file if the name differs.

📁 Suggested Project Structure
armor-safe-browsing/
│
├── main.py
├── background.png
├── chrome.png
├── README.md
└── requirements.txt (optional)


Example requirements.txt:

pywebview


Install all dependencies using:

pip install -r requirements.txt

🚨 Why Armor?

The modern web works on a risky assumption:

Any browser can access any website.

This exposes users to:

Phishing attacks

Malicious redirects

Script injection

URL-based data leaks

Bot-driven DDoS traffic

Armor flips this model.

Only trusted websites can be accessed — and only through the Armor browser.

🔐 Core Concept

Armor introduces a controlled web access environment where:

Websites must be verified and registered

Users can browse only via Armor

All traffic flows through a secure, monitored pipeline

Unsafe websites are blocked before loading

🧠 How It Works (High-Level)
User
 ↓
Armor Browser
 ↓
Security Check Engine
 ↓
Trusted Website Database
 ↓
Secure Rendering


If a website is verified → access is allowed

If a website is unsafe → access is blocked

If a service is needed → safe alternatives are suggested

🔑 Key Features
✅ Secure-Only Browsing

Access limited to verified domains

Unknown or unsafe websites never load

Eliminates accidental phishing

🔍 Safe Search Engine

Autocomplete suggestions only from trusted websites

Blocked websites never appear in search

Reduces user error while typing URLs

🔁 Service-Based Safe Alternatives

When a website is blocked, Armor:

Identifies the service type (e.g., social media, banking)

Suggests verified alternatives

Opens them only inside Armor

No raw URLs are exposed to the user.

🔐 Browser-Dependent Websites

Websites are bound to Armor using API keys

No API key → no access

Prevents unauthorized scraping and cloning

🧩 UID-Based User Access

Each user is assigned a unique identifier

Enables secure session handling

Improves auditing and abuse prevention

🕵️ Hidden URLs & API Paths

Users see only the main domain

API paths, object IDs, and query parameters are hidden

Prevents URL manipulation and IDOR attacks

🧹 Client-Side Protection

Inspection tools disabled

Script rewriting blocked

Redirect abuse prevented

🛑 Attacks Addressed
Attack Type	Armor’s Protection
DDoS	Centralized traffic routing, trusted services only
XSS	Script sanitization, restricted rendering
Phishing	Whitelisted domains, safe-only search results
IDOR	Hidden URLs, API-based navigation
🧪 Example Flow

User searches for a website

Armor checks the domain against its database

Website is flagged unsafe

Access is blocked

Armor suggests verified alternatives

User continues safely — without leaving Armor

🎯 Design Philosophy

Prevent, don’t react

Reduce attack surface

Security over convenience

Controlled freedom is safer freedom

Armor does not attempt to replace the entire internet —
it creates a safe subset of it.

🚀 Future Scope & Improvements

Dynamic trust scoring

AI-based phishing detection

Read-only restricted browsing mode

Enterprise / child-safe profiles

Admin dashboards & traffic analytics

Advanced browser sandboxing

⚠️ Disclaimer

Armor significantly reduces web attack risks within its environment.
It does not claim to eliminate all possible threats, but focuses on structural prevention at the browser level.

🧑‍💻 Project Status

🟡 Semi-functional prototype
🟢 Active development

🛡️ Armor

Because the safest attack is the one that never reaches you.
