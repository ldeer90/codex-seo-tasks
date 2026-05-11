"""
Drive organiser — moves Monday-linked files into correct client folders.
Uses service account with domain-wide delegation (impersonates seo@agents.digital).
Run: python3 scripts/drive_organise.py
"""

import sys
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

CREDENTIALS_FILE = "/Users/laurencedeer/Desktop/SEO Automation/seo-agency-work-267b2ddf0845.json"
SCOPES = ["https://www.googleapis.com/auth/drive"]
IMPERSONATE = "seo@agents.digital"   # change to hello@agents.digital if needed

# ── Client folder IDs (parent of 03 Audits / 07 Reports) ─────────────────────
CLIENT_PARENTS = {
    "Acorn Rentals":            "1M2MXfkRFsAMy5nFoM2m7miNOnjBEkvoj",
    "AVENUE Hampers":           "1LGXJQosWUROG5s4MVxbNaFgMvXFd90en",
    "Joe Rascal Ducati":        "157-ddATrb2byi0VMJYKg9JET4RzqIFFr",
    "Joe Rascal Harley":        "1XENbhUku8qau7HM5I7D9ivtIhrKpfU0s",
    "Little Shop of Happiness": "1wN3HSAcKrkXRLxuFA0OlHyGDqLDo9hx7",
    "Melani the Label":         "1HWLcsHS38P5u_d_vfrWux3LaRVln9iMJ",
    "Salad Servers":            "1VTJy6FaSqLkOyRxaf7ZiAQuoIQVXatyf",
    "Shop Rongrong":            "1TTxwqCl5JurXCyva9kGK9rz5v66YzaXU",
    "TravelKon":                "175zcM_g56_jtpU1m9bzAMFvLFahXAqS3",
    # Joe Rascal Global — will be created below
}

# ── Known subfolder IDs ───────────────────────────────────────────────────────
AUDITS = {
    "Acorn Rentals":            "1ZGPxHEygUPhes-0twOuoTkDBygIW-tAs",
    "AVENUE Hampers":           "1zmOww76CYrUhQOB_wcQvUKUbcFsFzYmF",
    "Joe Rascal Ducati":        "1zqzxqVT2aeJ1aahoGW3EM0qEoqomnB5x",
    "Joe Rascal Harley":        "1zea_22Ldi8q7QU0qkBs53HxZXwA68AIJ",
    "Little Shop of Happiness": "1MFU9-6X1uJys3IyIod7KFziJz40K5J8C",
    "Melani the Label":         "1j_tdnIT0mia1rJz0P2DU4zcs19jpQzS6",
    "Salad Servers":            "1JIyzafg5Q49ExzvJMqCR-Bsu1Hm16N9o",
    "Shop Rongrong":            "1ywpJIkNJddGRLdaGTiAnyDksoxP85pWD",
    "TravelKon":                "1aEbqpVIWbkaz8dkMZGKa14v6b5iJn_Jb",
}

REPORTS = {
    "Acorn Rentals":            "1gupoXp_cjGHm3ixSEIs3PFpKTb2ataJ2",
    "AVENUE Hampers":           "1VzFY_bDRX9jDNCeGzC53m5uKYsvOkacG",
    "Joe Rascal Ducati":        "1dzj65zJm15qNxV0AK0VyefNsr1prGkd2",
    "Joe Rascal Harley":        "1Vutz3IWesdKE21e4mw10P8V9Yw_cE6bD",
    "Little Shop of Happiness": "1D6IKdB56uC3uvgT9fOccT28Rl4zPo-qs",
    "Melani the Label":         "1Gfvxg4DuAzv_W5bGBJ62r09ap0woX6Eu",
    "Salad Servers":            "1RrX29zwEAiEv-SJFiqfSfkZAqJuKa6Sp",
    "Shop Rongrong":            "1K66iztEtBye5mCowq-chwTkMr0E1uati",
    "TravelKon":                "1HCuM9DP0xZ9sjms8Y6C1AZhgWap_A5pr",
}

# Will be populated after folder creation
KW_RESEARCH = {}
JR_GLOBAL_AUDITS = None
JR_GLOBAL_REPORTS = None
JR_GLOBAL_KW = None

# ── Files to move: (file_id, destination_dict_key, destination_type) ─────────
# destination_type: "audits", "reports", "kw_research"
FILES_TO_MOVE = [
    # Acorn Rentals
    ("1-mh5-PDbMTp8dkMseUjippq6qMju9MpQTpJVKxNlUnU", "Acorn Rentals", "audits"),   # Content recommendations
    ("10Be30AwlvFSwvnAEsBQCJ9eAVeNDtyvm",             "Acorn Rentals", "reports"),  # GSC Report
    ("1hyZ6qcUmT937zFtgqLXOADGWoEKTOmP7",            "Acorn Rentals", "audits"),   # Schema code
    ("1yQjs9j9z6PDobZ36YBfOHO1PmsGN8DW1",            "Acorn Rentals", "audits"),   # Audit Report

    # AVENUE Hampers
    ("1bFRLc2y855edY5VssPvPlmCrbZXvdo9L",            "AVENUE Hampers", "audits"),  # Audit Report
    ("1HooqfnCk_4jbdTosj4FG-bwpRbYqNmdn",            "AVENUE Hampers", "reports"), # GSC Report
    ("1oji2WQ5r6Ac23Id8uGrYg-tTkcoPebrT",            "AVENUE Hampers", "audits"),  # Schema code

    # Joe Rascal Ducati
    ("1RwBXZdqD4nxb3T42GR7wfGMFDQkCOPE6",            "Joe Rascal Ducati", "audits"),  # Audit Report
    ("1IFyz57-g4e3r-4zOXaks31FVjHYGIH63",            "Joe Rascal Ducati", "audits"),  # Schema code

    # Joe Rascal Harley (own files only — external-owned files skipped)
    ("1bR70VzXcU4vxsPiP5KsZcCgj3KXvohsb",            "Joe Rascal Harley", "audits"),  # Schema code

    # Little Shop of Happiness
    ("15yC4Hvm19FNtWwkKh8mFsXzrEfjiOt4F",            "Little Shop of Happiness", "audits"),  # Audit Report
    ("1009edLl4Os-G7EnvmFNaUkG2r4Xe8viz",            "Little Shop of Happiness", "reports"), # GSC Report
    ("1Oji2rjVsfBu2K4a9jq3IdtnVD0gu01wR",            "Little Shop of Happiness", "audits"),  # Schema code

    # Melani the Label
    ("1OKys7twZ3kDobzrfVDf9pIXZ-iCNnqBZ",            "Melani the Label", "audits"),  # Audit Report (May 8)
    ("1zaY-TcAin4RU1yLf8Y9m7dGjUzH7Z8tr",            "Melani the Label", "audits"),  # Audit Report (May 1)
    ("1yBvIBOyu_c45k8uXcJIfiTDlw_dhFc3yeZ3rbnnTTRo", "Melani the Label", "kw_research"),  # Keywords Research
    ("1gQ9J0gHG3cHclDG71DnGKNFnF0S_EfVo1PL3EihYAWg", "Melani the Label", "audits"),  # On-page Status Report

    # Salad Servers
    ("1mxDqoenJTRGCR7R-pw3zGVFS8XHisjL8",            "Salad Servers", "audits"),  # Audit Report
    ("1l0Fwr2ScyNtBvGNtV3TxyIOPPeVMT0wm",            "Salad Servers", "reports"), # GSC Report
    ("1PbHymLXy4NMjtYkt7PQiT29liB2F6Z9o",            "Salad Servers", "audits"),  # Schema code

    # Shop Rongrong
    ("1EEXWVHcp-NOOe8EA0KWOwjbjE_AGzHTB",            "Shop Rongrong", "audits"),  # Audit Report
    ("1FBdwsYQ-iHFnwEfngCD7K3rU7N8f8FPO",            "Shop Rongrong", "reports"), # GSC Report
    ("1g3YW4LN8bQLsQINn3-_7Te2zfY-hRPBA",            "Shop Rongrong", "audits"),  # Schema code
    ("1By5FYMSVqKThGIZxi3m5tFXxXrLJ1u6dX1QwhvWbff8","Shop Rongrong", "audits"),  # Website Suggestion Report
    ("1ZfKyBjNznVhqUdMJj7hBBFRV5mXUMsvGmAlo7UgG7O4","Shop Rongrong", "audits"),  # Collection Pages

    # TravelKon
    ("1dezYUb8BIVyg6HyatWtMRBe09lnntxO2",            "TravelKon", "audits"),  # Audit Report
    ("19bEUJT43E2O6BpAQHHpnRWB4HjAWE6l5",            "TravelKon", "reports"), # GSC Report
    ("1iVeyattwr3xcoX1MNEb8nManWJMqnaZR",             "TravelKon", "audits"),  # Schema code

    # Joe Rascal Global (target folder created at runtime)
    ("1Qir6dkdz_qJni61nqqHs2dvTPAO5lKMwXNyBnwb49J8","Joe Rascal Global", "kw_research"), # Keywords Research
    ("1uSGjj78EeR6uRX1EBy42XhfEFuU-Z9e9xzQrdoo8Wqw","Joe Rascal Global", "audits"),      # Suggestion Meta Tags
    ("12i1L0QJQM5qClZ2UNlzK8Vm4EjAaXf93SX0iXKFJo2o","Joe Rascal Global", "audits"),      # Suggested Meta tags and H1
]

# Multi-client keyword research sheet — copy once per client
MULTI_CLIENT_KW_ID = "1Le51GPhCt-Gb-DJLhmfs0I2V2ifuyIdSt0Vb1Pwvw0o"
MULTI_CLIENT_KW_CLIENTS = [
    "Shop Rongrong",
    "Salad Servers",
    "TravelKon",
    "Acorn Rentals",
    "Little Shop of Happiness",
]

# Joe Rascal Harley keyword research (external owner — we can only copy if shared)
JR_HARLEY_KW_ID = "1Hcm6XNWEaCNNtt_lYmniOD_e7mzdxb3d6QFWl4jog1M"

def build_service(impersonate=IMPERSONATE):
    creds = service_account.Credentials.from_service_account_file(
        CREDENTIALS_FILE, scopes=SCOPES
    )
    if impersonate:
        creds = creds.with_subject(impersonate)
    return build("drive", "v3", credentials=creds)


def create_folder(service, name, parent_id):
    meta = {
        "name": name,
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [parent_id],
    }
    f = service.files().create(body=meta, fields="id,name").execute()
    print(f"  📁 Created folder '{f['name']}' → {f['id']}")
    return f["id"]


def move_file(service, file_id, new_parent_id):
    """Move by adding new parent and removing old ones."""
    # get current parents
    meta = service.files().get(fileId=file_id, fields="name,parents").execute()
    old_parents = ",".join(meta.get("parents", []))
    result = service.files().update(
        fileId=file_id,
        addParents=new_parent_id,
        removeParents=old_parents,
        fields="id,name,parents",
    ).execute()
    return result


def copy_file(service, file_id, new_parent_id, new_name=None):
    body = {"parents": [new_parent_id]}
    if new_name:
        body["name"] = new_name
    result = service.files().copy(fileId=file_id, body=body, fields="id,name").execute()
    return result


def main():
    print("Authenticating…")
    try:
        svc = build_service(IMPERSONATE)
        # quick test
        svc.files().get(fileId="root", fields="id").execute()
        print(f"✅ Authenticated as {IMPERSONATE}\n")
    except Exception as e:
        print(f"❌ Auth failed as {IMPERSONATE}: {e}")
        print("Trying hello@agents.digital…")
        try:
            svc = build_service("hello@agents.digital")
            svc.files().get(fileId="root", fields="id").execute()
            print("✅ Authenticated as hello@agents.digital\n")
        except Exception as e2:
            print(f"❌ Auth also failed: {e2}")
            print("\nService account likely needs domain-wide delegation enabled.")
            print("Go to: Google Workspace Admin → Security → API Controls → Domain-wide Delegation")
            print("Add client ID for: codex-seo-automation@seo-agency-work.iam.gserviceaccount.com")
            print("Scope: https://www.googleapis.com/auth/drive")
            sys.exit(1)

    # ── Step 1: Create Joe Rascal Global folder structure ────────────────────
    print("── Step 1: Creating Joe Rascal Global folder structure ──")
    # Find the parent used by JR Ducati (157-ddATrb2byi0VMJYKg9JET4RzqIFFr's parent)
    jr_ducati_parent = "157-ddATrb2byi0VMJYKg9JET4RzqIFFr"
    try:
        ducati_meta = svc.files().get(fileId=jr_ducati_parent, fields="parents,name").execute()
        clients_parent = ducati_meta["parents"][0]
        print(f"  Clients parent folder: {clients_parent}")
    except Exception as e:
        print(f"  ⚠️  Could not find clients parent: {e}. Using JR Ducati parent directly.")
        clients_parent = jr_ducati_parent

    global JR_GLOBAL_AUDITS, JR_GLOBAL_REPORTS, JR_GLOBAL_KW
    jr_global_id = create_folder(svc, "Joe Rascal Global", clients_parent)
    JR_GLOBAL_AUDITS  = create_folder(svc, "03 Audits",           jr_global_id)
    JR_GLOBAL_REPORTS = create_folder(svc, "07 Reports",          jr_global_id)
    JR_GLOBAL_KW      = create_folder(svc, "04 Keyword Research", jr_global_id)

    CLIENT_PARENTS["Joe Rascal Global"] = jr_global_id
    AUDITS["Joe Rascal Global"]         = JR_GLOBAL_AUDITS
    REPORTS["Joe Rascal Global"]        = JR_GLOBAL_REPORTS
    KW_RESEARCH["Joe Rascal Global"]    = JR_GLOBAL_KW
    print()

    # ── Step 2: Create 04 Keyword Research subfolders for all other clients ──
    print("── Step 2: Creating 04 Keyword Research subfolders ──")
    kw_clients = [
        "Acorn Rentals", "AVENUE Hampers", "Joe Rascal Ducati",
        "Joe Rascal Harley", "Little Shop of Happiness", "Melani the Label",
        "Salad Servers", "Shop Rongrong", "TravelKon",
    ]
    for client in kw_clients:
        parent = CLIENT_PARENTS[client]
        folder_id = create_folder(svc, "04 Keyword Research", parent)
        KW_RESEARCH[client] = folder_id
    print()

    # ── Step 3: Move floating files into correct folders ─────────────────────
    print("── Step 3: Moving files ──")
    ok, skipped, failed = 0, 0, 0
    for file_id, client, dest_type in FILES_TO_MOVE:
        if dest_type == "audits":
            target = AUDITS.get(client)
        elif dest_type == "reports":
            target = REPORTS.get(client)
        elif dest_type == "kw_research":
            target = KW_RESEARCH.get(client)
        else:
            target = None

        if not target:
            print(f"  ⚠️  No target folder for {client}/{dest_type} — skipping {file_id}")
            skipped += 1
            continue

        try:
            result = move_file(svc, file_id, target)
            print(f"  ✅ Moved '{result['name']}' → {client}/{dest_type}")
            ok += 1
        except HttpError as e:
            print(f"  ❌ Failed to move {file_id} ({client}/{dest_type}): {e}")
            failed += 1

    print()

    # ── Step 4: Copy multi-client keyword research sheet per client ──────────
    print("── Step 4: Copying multi-client Keywords Research sheet per client ──")
    for client in MULTI_CLIENT_KW_CLIENTS:
        target = KW_RESEARCH.get(client)
        if not target:
            print(f"  ⚠️  No KW folder for {client} — skipping")
            continue
        try:
            result = copy_file(svc, MULTI_CLIENT_KW_ID, target, f"Keywords Research - {client}")
            print(f"  ✅ Copied Keywords Research → {client}/04 Keyword Research")
            ok += 1
        except HttpError as e:
            print(f"  ❌ Failed to copy for {client}: {e}")
            failed += 1

    # ── Step 5: Copy Joe Rascal Harley keyword research (external owner) ─────
    print()
    print("── Step 5: Attempting Joe Rascal Harley keyword research (external owner) ──")
    try:
        result = copy_file(svc, JR_HARLEY_KW_ID, KW_RESEARCH["Joe Rascal Harley"],
                           "Keywords Research - Joe Rascal Harley")
        print("  ✅ Copied JR Harley Keywords Research")
        ok += 1
    except HttpError as e:
        print(f"  ⚠️  Could not copy external-owned file: {e}")
        print("     Ask iteintegrated@gmail.com to share it or transfer ownership.")
        skipped += 1

    print()
    print(f"── Done: {ok} succeeded · {skipped} skipped · {failed} failed ──")


if __name__ == "__main__":
    main()
