# Troubleshoot Access

A tool returned 401, 403, or 404 from Google. Walk through this before changing anything.

## Step 1 — Get the actual error

Read the error message from the tool result, especially the status code and the property/folder ID it tried to reach.

## Step 2 — Confirm the routing

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

- `analytics.subject` — what the router decided.
- `analytics.source` — where the decision came from (`property`, `host`, `client`, `default`).
- `analytics.validated` — whether the chosen subject can actually read the property.
- `candidates` — the full set the server can try.

## Step 3 — Diagnose

| Symptom | Likely cause | Fix |
|---|---|---|
| `analytics.validated: false` even after fallback | Neither delegated subject can read this GA4 property | Add the delegated user in GA4 Admin → Property Access. Or add the service account directly. |
| Right subject but Drive 403 on output | The output subject can't see `GOOGLE_DRIVE_REPORTS_FOLDER_ID` | Share the folder with the output subject (Editor). |
| Wrong subject chosen | `site-access.json` doesn't have a rule, or has a stale rule | Edit `config/site-access.json` and add an explicit `properties` or `clients` entry. |
| 404 on a property ID | Wrong ID or the property was deleted | Check `docs/platform-reference.md` for the current ID. Regenerate if stale. |
| 401 immediately after the service-account JSON was rotated | Local cache of credentials | Restart the MCP server (Codex will re-launch on the next call). |

## Step 4 — Don't paper over it

Do not pass `validate_ga4_access=false` to make the warning go away. The server will silently report data from whichever subject the router picked, but downstream calls inside `create_combined_seo_report` still need access — they will fail later, after burning Firecrawl credits.

## Step 5 — Document the fix

If you changed `config/site-access.json` or granted new GA4/Drive access, note it in the relevant client brief under Notes.
