"""
drive_auto_organise.py
─────────────────────
Fully dynamic Drive organiser for Agents Digital SEO work.

What it does:
  1. Scans all "inbox" locations (root, _ Root Cleanup, any other folder you add)
  2. Classifies each file by client (from filename keywords) and type (audit/report/kw)
  3. Moves it to the right client subfolder, creating missing subfolders if needed
  4. Anything it can't classify goes into _ Root Cleanup for manual review

Adding a new client:
  - Add an entry to CLIENTS with their folder IDs
  - If subfolders don't exist yet, set the value to None — the script will create them

Run:
  python3 scripts/drive_auto_organise.py
  python3 scripts/drive_auto_organise.py --dry-run   ← preview only, no moves
"""

import argparse
import sys
from google.oauth2 import service_account
from googleapiclient.discovery import build

# ── Auth ──────────────────────────────────────────────────────────────────────
CREDENTIALS_FILE = "/Users/laurencedeer/Desktop/SEO Automation/seo-agency-work-267b2ddf0845.json"
SCOPES           = ["https://www.googleapis.com/auth/drive"]
ACCOUNTS         = ["seo@agents.digital", "hello@agents.digital"]  # tried in order

# ── Agents Digital root folder ────────────────────────────────────────────────
AGENTS_DIGITAL_ID   = "1ZpzgOmzDHmb01ebq_N0lejCI74r3s1jd"
ROOT_CLEANUP_NAME   = "_ Root Cleanup"

# ── Client config ─────────────────────────────────────────────────────────────
# keywords: lowercase strings that identify this client in a filename
# audits / reports / kw_research: Drive folder IDs (None = create on first use)
# parent: the client's top-level folder (used to create missing subfolders)
CLIENTS = {
    "Acorn Rentals": {
        "keywords":     ["acorn"],
        "parent":       "1M2MXfkRFsAMy5nFoM2m7miNOnjBEkvoj",
        "audits":       "1ZGPxHEygUPhes-0twOuoTkDBygIW-tAs",
        "reports":      "1gupoXp_cjGHm3ixSEIs3PFpKTb2ataJ2",
        "kw_research":  "1Zr57NlGY2zATN45YfRyXxlgjSLM9AHTf",
    },
    "AVENUE Hampers": {
        "keywords":     ["avenue", "hampers"],
        "parent":       "1LGXJQosWUROG5s4MVxbNaFgMvXFd90en",
        "audits":       "1zmOww76CYrUhQOB_wcQvUKUbcFsFzYmF",
        "reports":      "1VzFY_bDRX9jDNCeGzC53m5uKYsvOkacG",
        "kw_research":  "1jndv9gMnSbLhiEPF_a-9m2TPqGFsdmZH",
    },
    "Joe Rascal Ducati": {
        "keywords":     ["ducati"],
        "parent":       "157-ddATrb2byi0VMJYKg9JET4RzqIFFr",
        "audits":       "1zqzxqVT2aeJ1aahoGW3EM0qEoqomnB5x",
        "reports":      "1dzj65zJm15qNxV0AK0VyefNsr1prGkd2",
        "kw_research":  "1ztedt6U1nSJrcVgYQ4MoIUbKU2aSm2Y-",
    },
    "Joe Rascal Harley": {
        "keywords":     ["harley"],
        "parent":       "1XENbhUku8qau7HM5I7D9ivtIhrKpfU0s",
        "audits":       "1zea_22Ldi8q7QU0qkBs53HxZXwA68AIJ",
        "reports":      "1Vutz3IWesdKE21e4mw10P8V9Yw_cE6bD",
        "kw_research":  "1Nj3odpXvbn8bDAz7LAYtGR60uiWO_LqE",
    },
    "Joe Rascal Global": {
        "keywords":     ["joerascal.com", "joe rascal global", "joerascal global"],
        "parent":       "1H1I3HVwTXmPCXQhJCIwipRC2j_Bngc-a",
        "audits":       "1CyPmRsq5EcYOGpbXFIwByTV6EYrzASs3",
        "reports":      "1mAkZSx1_AOr4ZGhgZYwBYknmX8vYgLJa",
        "kw_research":  "1kLk7kohaBUr0_V-b5Z-YngZ8dRSiwRky",
    },
    "Little Shop of Happiness": {
        "keywords":     ["littleshop", "little shop", "happiness"],
        "parent":       "1wN3HSAcKrkXRLxuFA0OlHyGDqLDo9hx7",
        "audits":       "1MFU9-6X1uJys3IyIod7KFziJz40K5J8C",
        "reports":      "1D6IKdB56uC3uvgT9fOccT28Rl4zPo-qs",
        "kw_research":  "1QnqGSpvMv0MELxINJkwNosljG1OWuPXm",
    },
    "Melani the Label": {
        "keywords":     ["melani"],
        "parent":       "1HWLcsHS38P5u_d_vfrWux3LaRVln9iMJ",
        "audits":       "1j_tdnIT0mia1rJz0P2DU4zcs19jpQzS6",
        "reports":      "1Gfvxg4DuAzv_W5bGBJ62r09ap0woX6Eu",
        "kw_research":  "1UQfNcteFJkB4Ckk3tcCJZjLhUgTKHPSC",
    },
    "Salad Servers": {
        "keywords":     ["salad"],
        "parent":       "1VTJy6FaSqLkOyRxaf7ZiAQuoIQVXatyf",
        "audits":       "1JIyzafg5Q49ExzvJMqCR-Bsu1Hm16N9o",
        "reports":      "1RrX29zwEAiEv-SJFiqfSfkZAqJuKa6Sp",
        "kw_research":  "1Wanu5peclOfUNJcUwGVub6riGxNfuktw",
    },
    "Shop Rongrong": {
        "keywords":     ["shoprongrong", "shop rongrong", "rongrong"],
        "parent":       "1TTxwqCl5JurXCyva9kGK9rz5v66YzaXU",
        "audits":       "1ywpJIkNJddGRLdaGTiAnyDksoxP85pWD",
        "reports":      "1K66iztEtBye5mCowq-chwTkMr0E1uati",
        "kw_research":  "1_6c6lFxotBjpuJgPWswFuaX5HLudSnxy",
    },
    "TravelKon": {
        "keywords":     ["travelkon", "travel kon"],
        "parent":       "175zcM_g56_jtpU1m9bzAMFvLFahXAqS3",
        "audits":       "1aEbqpVIWbkaz8dkMZGKa14v6b5iJn_Jb",
        "reports":      "1HCuM9DP0xZ9sjms8Y6C1AZhgWap_A5pr",
        "kw_research":  "1nuLYAk6bVAZ_uY8EsxCWfM1-Syl2Q57g",
    },
}

# ── File-type classification ───────────────────────────────────────────────────
# First match wins. Add new patterns here as new deliverable types emerge.
TYPE_RULES = [
    ("kw_research", ["keywords research", "keyword research", "keyword positions",
                     "keyword mapping", "positions_detailed", "export_research",
                     "avenuehampers.com.au-keyword"]),
    ("reports",     ["google search console", "gsc report", "coverage-drilldown",
                     "coverage-valid", "coverage-2", "performance on search",
                     "monthly report", "analysis of", "drilldown", "seo dashboard",
                     "project dashboard", "product snippets", "search console performance"]),
    ("audits",      ["audit report", "detailed audit", "schema code", "on page sheet",
                     "on-page sheet", "on-page status", "suggestion report",
                     "website suggestion", "collection pages", "content recommend",
                     "screaming frog", "initial crawl", "footer suggestion",
                     "duplicate h1", "meta tags", "suggested meta", "blogs to unpublish",
                     "benchmarking", "technical seo", "outlinks", "4xx error",
                     "competitors of", "extract collection", "keyword mapping",
                     "meta data improvements", "collection overlaps", "empty categor",
                     "empty collection", "monday task", "missing products",
                     "meta data", "worksheet", "site structure"]),
]

FOLDER_MIME = "application/vnd.google-apps.folder"

# ── Helpers ───────────────────────────────────────────────────────────────────

def build_service(impersonate):
    creds = service_account.Credentials.from_service_account_file(
        CREDENTIALS_FILE, scopes=SCOPES
    ).with_subject(impersonate)
    return build("drive", "v3", credentials=creds, cache_discovery=False)


def get_or_create_folder(svc, name, parent_id, dry_run=False):
    """Return existing folder ID or create it."""
    res = svc.files().list(
        q=f"name='{name}' and '{parent_id}' in parents and mimeType='{FOLDER_MIME}' and trashed=false",
        fields="files(id,name)", pageSize=1,
    ).execute()
    if res["files"]:
        return res["files"][0]["id"]
    if dry_run:
        return f"<would-create:{name}>"
    f = svc.files().create(
        body={"name": name, "mimeType": FOLDER_MIME, "parents": [parent_id]},
        fields="id,name",
    ).execute()
    print(f"    📁 Created subfolder '{name}'")
    return f["id"]


def list_folder(svc, folder_id):
    files, token = [], None
    while True:
        res = svc.files().list(
            q=f"'{folder_id}' in parents and mimeType!='{FOLDER_MIME}' and trashed=false",
            fields="nextPageToken,files(id,name,parents,mimeType)",
            pageSize=200, pageToken=token,
        ).execute()
        files.extend(res.get("files", []))
        token = res.get("nextPageToken")
        if not token:
            break
    return files


def classify(name):
    """Return (client_name, dest_type) or (None, None) if unrecognised."""
    lower = name.lower()

    # client
    client = None
    for cname, cfg in CLIENTS.items():
        if any(k in lower for k in cfg["keywords"]):
            client = cname
            break

    # type
    dest = None
    for dtype, patterns in TYPE_RULES:
        if any(p in lower for p in patterns):
            dest = dtype
            break

    return client, dest


def move(svc, file_id, old_parents, new_parent, dry_run):
    if dry_run:
        return
    svc.files().update(
        fileId=file_id,
        addParents=new_parent,
        removeParents=",".join(old_parents),
        fields="id",
    ).execute()


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Preview without moving")
    args = parser.parse_args()
    DRY = args.dry_run
    if DRY:
        print("🔍 DRY RUN — no files will be moved\n")

    # Authenticate
    svc = None
    for acct in ACCOUNTS:
        try:
            s = build_service(acct)
            s.files().get(fileId="root", fields="id").execute()
            svc = s
            print(f"✅ Authenticated as {acct}\n")
            break
        except Exception as e:
            print(f"⚠️  {acct} failed: {e}")
    if not svc:
        print("❌ Could not authenticate. Check domain-wide delegation.")
        sys.exit(1)

    # Ensure _ Root Cleanup exists
    cleanup_id = get_or_create_folder(svc, ROOT_CLEANUP_NAME, AGENTS_DIGITAL_ID, DRY)

    # Build set of all known "correct" folder IDs
    known_folders = {AGENTS_DIGITAL_ID, cleanup_id}
    for cfg in CLIENTS.values():
        for key in ("parent", "audits", "reports", "kw_research"):
            if cfg.get(key):
                known_folders.add(cfg[key])

    # Collect files to process: root + cleanup folder
    inbox = []
    print("Scanning inbox locations…")
    for label, fid in [("root", "root"), ("_ Root Cleanup", cleanup_id)]:
        batch = list_folder(svc, fid)
        print(f"  {label}: {len(batch)} files")
        inbox.extend(batch)

    if not inbox:
        print("\nNothing to organise. ✨")
        return

    print(f"\nClassifying and moving {len(inbox)} files…\n")
    moved = skipped = unclassified = 0

    for f in inbox:
        name     = f["name"]
        file_id  = f["id"]
        parents  = f.get("parents", [])
        client, dest_type = classify(name)

        if client and dest_type:
            cfg        = CLIENTS[client]
            folder_key = dest_type          # "audits" | "reports" | "kw_research"
            target_id  = cfg.get(folder_key)

            if not target_id:
                # Create the subfolder on the fly
                subfolder_names = {"audits": "03 Audits", "reports": "07 Reports",
                                   "kw_research": "04 Keyword Research"}
                target_id = get_or_create_folder(
                    svc, subfolder_names[folder_key], cfg["parent"], DRY
                )
                if not DRY:
                    cfg[folder_key] = target_id   # cache for this run

            # Skip if already in the right place
            if target_id in parents:
                print(f"  ✓  Already filed: {name}")
                skipped += 1
                continue

            action = "Would move" if DRY else "Moving"
            print(f"  ✅ {action}: '{name}' → {client} / {folder_key}")
            move(svc, file_id, parents, target_id, DRY)
            moved += 1

        else:
            # Can't classify — send to cleanup if not already there
            if cleanup_id in parents:
                print(f"  ⚠️  Unclassified (already in cleanup): {name}")
            else:
                action = "Would send" if DRY else "Sending"
                reason = "no client match" if not client else "no type match"
                print(f"  📦 {action} to cleanup ({reason}): {name}")
                move(svc, file_id, parents, cleanup_id, DRY)
            unclassified += 1

    print(f"\n── Done: {moved} moved · {skipped} already correct · {unclassified} unclassified ──")
    if unclassified:
        print(f"   Review unclassified files in: Agents Digital / {ROOT_CLEANUP_NAME}")


if __name__ == "__main__":
    main()
