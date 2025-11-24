import os
import json
import threading
import time
from datetime import datetime
from uuid import uuid4

# ===============================================================
# CONFIGURATION
# ===============================================================
DATASET = r"D:\AI-Powered-RegulatoryCompliance-Checker-for-Contracts\Dataset"
REG_FILE = os.path.join(DATASET, "regulations.json")
CONTRACT_FILE = os.path.join(DATASET, "contracts_index.json")
CONTRACT_DIR = os.path.join(DATASET, "contracts")
SCHEDULER_INTERVAL = 30

stop_event = threading.Event()
scheduler_thread = None


# ===============================================================
# FILE SETUP
# ===============================================================
def ensure_dirs():
    if os.path.exists(CONTRACT_DIR) is False:
        os.makedirs(CONTRACT_DIR, exist_ok=True)


def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def load_json(path):
    with open(path, "r") as f:
        return json.load(f)


# ===============================================================
# RESET + CREATE DATASET EVERY RUN
# ===============================================================
def init_sample_data():
    # Remove old data
    if os.path.exists(CONTRACT_DIR):
        for f in os.listdir(CONTRACT_DIR):
            os.remove(os.path.join(CONTRACT_DIR, f))

    # Initial regulations
    regs = [
        {
            "id": "REG-EU-001",
            "title": "GDPR Consent Logging",
            "jurisdiction": "EU",
            "summary": "Requires timestamp-based consent tracking.",
            "keywords": ["consent", "personal data", "logging"]
        },
        {
            "id": "REG-IN-001",
            "title": "India Data Localisation",
            "jurisdiction": "IN",
            "summary": "Requires sensitive personal data stored within India.",
            "keywords": ["localisation", "cross-border", "personal data"]
        },
    ]
    save_json(REG_FILE, regs)

    # Initial contracts
    contracts = {
        "CT001": {
            "name": "EU SaaS Service Agreement",
            "jurisdiction": "EU",
            "version": 1,
            "file": "contracts/CT001-v1.txt",
            "applied": []
        },
        "CT002": {
            "name": "India Hosting Contract",
            "jurisdiction": "IN",
            "version": 1,
            "file": "contracts/CT002-v1.txt",
            "applied": []
        }
    }
    save_json(CONTRACT_FILE, contracts)

    # Create fresh contract text files
    with open(os.path.join(DATASET, contracts["CT001"]["file"]), "w") as f:
        f.write("Processing of personal data is allowed. Consent handled by customer.")

    with open(os.path.join(DATASET, contracts["CT002"]["file"]), "w") as f:
        f.write("Data stored in India. Cross-border transfer allowed with safeguards.")

    print("[DATASET RESET] Fresh dataset created successfully")


# ===============================================================
# LOGIC
# ===============================================================
def read_contract(meta):
    with open(os.path.join(DATASET, meta["file"]), "r") as f:
        return f.read().lower()


def relevance(reg, meta, text):
    score = 0
    matches = []
    for kw in reg["keywords"]:
        if kw in text:
            score += 2
            matches.append(kw)
    if reg["jurisdiction"].lower() in ["global", meta["jurisdiction"].lower()]:
        score += 3
        matches.append(f"jurisdiction:{reg['jurisdiction']}")
    return score, matches


def apply_regulation(reg, cid):
    index = load_json(CONTRACT_FILE)
    meta = index[cid]

    if reg["id"] in meta["applied"]:
        print("⚠ Regulation already applied.")
        return

    text = read_contract(meta)
    new_version = meta["version"] + 1
    new_file = f"contracts/{cid}-v{new_version}.txt"
    amendment = (
        f"\n\n--- Amendment on {datetime.utcnow().isoformat()} ---\n"
        f"Applied Regulation: {reg['title']}\n"
        f"Summary: {reg['summary']}\n"
    )
    with open(os.path.join(DATASET, new_file), "w") as f:
        f.write(text + amendment)

    meta["version"] = new_version
    meta["file"] = new_file
    meta["applied"].append(reg["id"])
    index[cid] = meta
    save_json(CONTRACT_FILE, index)

    print(f"✔ Regulation applied — new version created: v{new_version}")


def fetch_mock_regulation():
    regs = load_json(REG_FILE)
    new = {
        "id": f"REG-MOCK-{uuid4().hex[:6]}",
        "title": "Global Privacy Profiling Disclosure",
        "jurisdiction": "GLOBAL",
        "summary": "Requires organisations to notify users of automated profiling.",
        "keywords": ["profiling", "notice", "transparency"]
    }
    regs.append(new)
    save_json(REG_FILE, regs)
    print(f"🌍 New mock regulation fetched → {new['id']}")


def scheduler_job():
    print("[Scheduler running...]")
    while not stop_event.is_set():
        fetch_mock_regulation()
        time.sleep(SCHEDULER_INTERVAL)
    print("[Scheduler stopped]")


def toggle_scheduler():
    global scheduler_thread
    if scheduler_thread and scheduler_thread.is_alive():
        stop_event.set()
        print("⏹ Scheduler stopping...")
    else:
        stop_event.clear()
        scheduler_thread = threading.Thread(target=scheduler_job, daemon=True)
        scheduler_thread.start()
        print("▶ Scheduler started")


# ===============================================================
# MENU
# ===============================================================
def main():
    ensure_dirs()
    init_sample_data()   # always update dataset every run

    while True:
        print("\n=== Regulatory Compliance Tracker ===")
        print("1) View regulations")
        print("2) View contracts")
        print("3) Analyse relevance between regulations & contracts")
        print("4) Apply regulation to contract")
        print("5) Fetch mock regulation")
        print("6) Start/Stop scheduler")
        print("0) Exit")

        c = input("Choose: ").strip()
        if c == "1":
            for r in load_json(REG_FILE):
                print("•", r["id"], "→", r["title"])
        elif c == "2":
            for cid, meta in load_json(CONTRACT_FILE).items():
                print(f"• {cid} → {meta['name']} (v{meta['version']})")
        elif c == "3":
            regs = load_json(REG_FILE)
            idx = load_json(CONTRACT_FILE)
            for cid, meta in idx.items():
                text = read_contract(meta)
                print(f"\nContract {cid}:")
                for r in regs:
                    score, hits = relevance(r, meta, text)
                    if score > 0:
                        print(f"  → {r['id']} | score={score} | matches={hits}")
                    else:
                        print(f"  → {r['id']} | no influence")
        elif c == "4":
            regs = load_json(REG_FILE)
            idx = load_json(CONTRACT_FILE)
            print("\nAvailable regulations:")
            for r in regs:
                print(" -", r["id"])
            rid = input("Enter regulation ID: ").strip()
            reg = next((x for x in regs if x["id"] == rid), None)
            if not reg:
                print("❌ Invalid regulation")
                continue
            print("\nAvailable contracts:")
            for key in idx:
                print(" -", key)
            cid = input("Enter contract ID: ").strip()
            if cid not in idx:
                print("❌ Invalid contract")
                continue
            apply_regulation(reg, cid)
        elif c == "5":
            fetch_mock_regulation()
        elif c == "6":
            toggle_scheduler()
        elif c == "0":
            stop_event.set()
            print("👋 Goodbye")
            break
        else:
            print("❌ Invalid choice")


if __name__ == "__main__":
    main()
