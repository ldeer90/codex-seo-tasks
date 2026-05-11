---
description: Diagnose Google 401/403/404 access errors before changing anything
argument-hint: <client> [error or context]
---

# LD SEO — Troubleshoot Access

A tool returned 401, 403, or 404 from Google. Walk through this before changing anything.

## MCPs / APIs used

| Service | Tools / endpoints |
|---|---|
| **MCP server tool** | `resolve_google_access_subject(validate_ga4_access=True)` — returns subject, source, and validation result |
| **Google Drive MCP** | `get_file_permissions`, `get_file_metadata` (when error is on Drive file/folder) |
| **GA4 Admin (manual)** | Property Access Management — add the delegated subject if validation fails |
| **Files inspected** | `config/site-access.json` (routing map), `docs/agent/clients/<client>.json` (sidecar) |

## How to invoke

```
/ldseo-troubleshoot <client> [error or context]
```

Examples:

```
/ldseo-troubleshoot melani-the-label 403 on GA4 read
/ldseo-troubleshoot joe-rascal Drive folder not found
```

## Required reading

`docs/agent/workflows/troubleshoot-access.md`

## Steps

### Step 1 — Get the actual error

Read the error from the tool result. Note status code and the property/folder ID it tried to reach.

### Step 2 — Confirm the routing

```json
// resolve_google_access_subject
{
  "client_name": "<client>",
  "website_url": "<site>",
  "ga4_property_id": "<property if known>",
  "validate_ga4_access": true
}
```

Look at:
- `analytics.subject` — what the router decided
- `analytics.source` — where the decision came from
- `analytics.validated` — whether the chosen subject can read the property

### Step 3 — Check service account access

If validated is `false`, the delegated subject doesn't have access. Either:
- Add the subject to the GA4 property in GA4 Admin → Property Access Management
- Add the subject to the Drive folder with at least Editor

### Step 4 — Check `config/site-access.json` mapping

Confirm the client's host + property ID + subject mapping is correct.

## Hard rules

- Diagnose before fixing — don't change config until you know what's broken
- Service account itself does not need direct access — domain-wide delegation handles impersonation
- Document the resolution in the client sidecar's `qa.access_notes` for future runs
