"""
Moves all loose files from My Drive root into a new '_Root Cleanup' folder
inside the Agents Digital folder. Leaves folders in place.
"""

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

CREDENTIALS_FILE = "/Users/laurencedeer/Desktop/SEO Automation/seo-agency-work-267b2ddf0845.json"
SCOPES = ["https://www.googleapis.com/auth/drive"]
IMPERSONATE = "hello@agents.digital"

AGENTS_DIGITAL_ID = "1ZpzgOmzDHmb01ebq_N0lejCI74r3s1jd"
ROOT_ID = "root"
FOLDER_MIME = "application/vnd.google-apps.folder"
CLEANUP_FOLDER_NAME = "_ Root Cleanup"

def build_service():
    creds = service_account.Credentials.from_service_account_file(
        CREDENTIALS_FILE, scopes=SCOPES
    ).with_subject(IMPERSONATE)
    return build("drive", "v3", credentials=creds)


def get_all_root_files(svc):
    """Return all non-folder files sitting directly in My Drive root."""
    files = []
    page_token = None
    while True:
        resp = svc.files().list(
            q=f"'{ROOT_ID}' in parents and mimeType != '{FOLDER_MIME}' and trashed = false",
            fields="nextPageToken, files(id, name, parents, mimeType)",
            pageSize=100,
            pageToken=page_token,
        ).execute()
        files.extend(resp.get("files", []))
        page_token = resp.get("nextPageToken")
        if not page_token:
            break
    return files


def move_file(svc, file_id, new_parent_id, old_parents):
    return svc.files().update(
        fileId=file_id,
        addParents=new_parent_id,
        removeParents=",".join(old_parents),
        fields="id, name",
    ).execute()


def main():
    print("Authenticating…")
    svc = build_service()
    svc.files().get(fileId="root", fields="id").execute()
    print(f"✅ Authenticated as {IMPERSONATE}\n")

    # Create cleanup folder inside Agents Digital
    print(f"Creating '{CLEANUP_FOLDER_NAME}' inside Agents Digital…")
    folder = svc.files().create(
        body={
            "name": CLEANUP_FOLDER_NAME,
            "mimeType": FOLDER_MIME,
            "parents": [AGENTS_DIGITAL_ID],
        },
        fields="id, name",
    ).execute()
    cleanup_id = folder["id"]
    print(f"  📁 Created: {folder['name']} ({cleanup_id})\n")

    # Get all loose files in root
    print("Scanning root for loose files…")
    loose = get_all_root_files(svc)
    print(f"  Found {len(loose)} files to move\n")

    ok = failed = 0
    for f in loose:
        try:
            result = move_file(svc, f["id"], cleanup_id, f.get("parents", []))
            print(f"  ✅ {result['name']}")
            ok += 1
        except HttpError as e:
            print(f"  ❌ {f['name']}: {e}")
            failed += 1

    print(f"\n── Done: {ok} moved · {failed} failed ──")
    print(f"\nAll files are now in: Agents Digital / {CLEANUP_FOLDER_NAME}")
    print(f"Folder link: https://drive.google.com/drive/folders/{cleanup_id}")


if __name__ == "__main__":
    main()
