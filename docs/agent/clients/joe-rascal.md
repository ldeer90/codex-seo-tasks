# Joe Rascal (parent group)

Joe Rascal is the parent client; Joe Rascal Harley, Joe Rascal Ducati, and Joe Rascal Global are siblings under it. Each has its own brief.

## Routing
- `client_name`: `Joe Rascal Harley` (parent fallback in `site-access.json` is `joe rascal harley` → `seo@agents.digital`).
- For top-level Joe Rascal work without a sub-brand, pass `Joe Rascal Harley` as `client_name` since the router has no separate `joe rascal` key. Use the website URL or property ID to differentiate the sub-brand at runtime.

## Drive
- Top-level folder: `Agents Digital / Clients / Joe Rascal`
- Folder ID: `14gHf6UZjgZ751CUP6iLz3Sf6WTTQBWSN`
- Sibling folders: `Joe Rascal Ducati` (`157-...`), `Joe Rascal Harley` (`1XENbhUku8qau7HM5I7D9ivtIhrKpfU0s`).

## Drive subfolders
Scan failed 2026-05-08 due to typo in folder ID (lowercase `n` vs uppercase `N`). ID confirmed correct from Drive URL on 2026-05-08.

Re-run `scan-client-folders` to populate subfolder data:
```bash
.venv/bin/python -m seo_automation_mcp.platform_inventory --client-folders
```

| Subfolder | ID |
|---|---|
| 07 Reports / SEO Reports | ⚠ pending — run scan then create inside `07 Reports` |
| 07 Reports / Benchmarks | ⚠ pending — run scan then create inside `07 Reports` |

Until `SEO Reports` is created, reports fall back to `GOOGLE_DRIVE_REPORTS_FOLDER_ID`.

## Monday
- Workspace: Main workspace
- Parent board: Joe Rascal (`5026853960`) — 9 items, 3 groups, 5 columns
- Subitems: `5026854299`
- Sibling boards: Joe Rascal Ducati (`5025418481`), Joe Rascal Harley (`5025418382`).

## Sub-brand summary

| Sub-brand | GA4 property | Website | Brief |
|---|---|---|---|
| Joe Rascal Harley | `513354197` | `joerascalharley.com.au` | [joe-rascal-harley.md](joe-rascal-harley.md) |
| Joe Rascal Ducati (stream on Ducati Melbourne property) | `402313624` | `joerascalducati.com.au` | [ducati-melbourne.md](ducati-melbourne.md) |
| Joe Rascal Global | `525910399` | `joerascal.com` | [joe-rascal-global.md](joe-rascal-global.md) |

## Notes
- When the user says just "Joe Rascal" without qualifier, ask which sub-brand. The default behaviour without confirmation is unsafe because each sub-brand has a different domain and GA4 property.
