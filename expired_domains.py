import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# =========================
# GOOGLE SHEET AYARLARI
# =========================
CREDS_FILE = "service_account.json"
SPREADSHEET_NAME = "Expired Domains SEO"
BUY_SHEET_NAME = "Buy_List"

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_FILE, scope)
client = gspread.authorize(creds)

spreadsheet = client.open(SPREADSHEET_NAME)
main_ws = spreadsheet.sheet1

try:
    buy_ws = spreadsheet.worksheet(BUY_SHEET_NAME)
except:
    buy_ws = spreadsheet.add_worksheet(
        title=BUY_SHEET_NAME, rows="1000", cols="10"
    )

# =========================
# SCRAPER AYARLARI
# =========================
EXPIRED_URL = "https://www.expireddomains.net/expired-domains/"
WAYBACK_API = "https://archive.org/wayback/available"

HEADERS = {"User-Agent": "Mozilla/5.0"}

SPAM_KEYWORDS = [
    "casino", "bet", "poker", "adult", "sex",
    "viagra", "pharma", "loan", "crypto"
]

NICHES = {
    "tech": ["software", "tech", "app", "cloud"],
    "health": ["health", "fitness", "diet"],
    "finance": ["finance", "loan", "money", "invest"],
    "travel": ["travel", "hotel", "tour"],
    "ecommerce": ["shop", "store", "buy"]
}

# =========================
# YARDIMCI FONKSİYONLAR
# =========================
def get_existing_domains(sheet):
    try:
        return set(sheet.col_values(1))
    except:
        return set()

def append_header(sheet):
    if sheet.row_count == 1:
        sheet.append_row(
            ["Domain", "SEO Score", "Niche", "Status", "Date"]
        )

def scrape_domains(pages=2):
    domains = []
    for page in range(1, pages + 1):
        url = f"{EXPIRED_URL}?start={(page - 1) * 25}"
        r = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(r.text, "lxml")
        table = soup.find("table", class_="base1")
        if not table:
            continue
        for row in table.find_all("tr")[1:]:
            cols = row.find_all("td")
            if len(cols) >= 2:
                domains.append(cols[0].text.strip())
    return domains

def wayback_check(domain):
    r = requests.get(WAYBACK_API, params={"url": domain}, headers=HEADERS)
    snap = r.json().get("archived_snapshots", {}).get("closest")
    if snap and snap.get("available"):
        return True, snap.get("url"), snap.get("timestamp")
    return False, None, None

def spam_check(snapshot_url):
    try:
        r = requests.get(snapshot_url, headers=HEADERS, timeout=10)
        text = r.text.lower()
        return any(word in text for word in SPAM_KEYWORDS)
    except:
        return True

def backlink_estimate(snapshot_url):
    try:
        r = requests.get(snapshot_url, timeout=10)
        soup = BeautifulSoup(r.text, "lxml")
        links = soup.find_all("a")
        return min(len(links) * 2, 20)
    except:
        return 0

def detect_niche(text):
    text = text.lower()
    for niche, words in NICHES.items():
        if any(w in text for w in words):
            return niche
    return "general"

def seo_score(domain):
    score = 0
    exists, snap_url, timestamp = wayback_check(domain)

    if not exists:
        return 0, "NO_HISTORY", "unknown"

    score += 40

    spam = spam_check(snap_url)
    if not spam:
        score += 40
    else:
        score -= 30

    backlink_score = backlink_estimate(snap_url)
    score += backlink_score

    niche = "general"
    try:
        r = requests.get(snap_url, timeout=10)
        niche = detect_niche(r.text)
    except:
        pass

    try:
        age = datetime.now().year - int(timestamp[:4])
        score += 20 if age >= 5 else 10 if age >= 2 else 0
    except:
        pass

    return score, "OK", niche

# =========================
# ANA ÇALIŞMA
# =========================
def run(pages=2):
    append_header(main_ws)
    append_header(buy_ws)

    existing_main = get_existing_domains(main_ws)
    existing_buy = get_existing_domains(buy_ws)

    domains = scrape_domains(pages)
    saved_rows = []

    for d in domains:
        if d in existing_main:
            continue

        score, status, niche = seo_score(d)
        if score < 60:
            continue

        today = datetime.now().strftime("%Y-%m-%d")
        row = [d, score, niche, status, today]

        main_ws.append_row(row)
        if d not in existing_buy:
            buy_ws.append_row(row)

        saved_rows.append(row)
        print(f"✔ {d} | Score: {score} | Niche: {niche}")

    if saved_rows:
        df = pd.DataFrame(
            saved_rows,
            columns=["domain", "seo_score", "niche", "status", "date"]
        )
        df.to_csv("seo_checked_domains.csv", index=False, encoding="utf-8-sig")

    print(f"\nToplam eklenen domain: {len(saved_rows)}")

# =========================
if __name__ == "__main__":
    run(pages=2)
