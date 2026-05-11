# Joe Rascal Global

## Routing
- `client_name`: `Joe Rascal Harley` — fallback because there is no dedicated `joe rascal global` key in `site-access.json`. The site-access map covers Joe Rascal Global through the Harley client mapping.
- Analytics subject: `seo@agents.digital` (visible to both subjects).
- Output subject: `hello@agents.digital`.
- Action item: add a `joe rascal global` key to `config/site-access.json` if reports for this site become a regular thing.

## GA4
- Account: Joe Rascal Harley
- Property: Joe Rascal Global - GA4
- Property ID: `properties/525910399`
- Web stream: `Joe Rascal Global Website` — `https://joerascal.com` (measurement ID `G-681P69RP8Y`)

## Web
- Primary URL: `https://joerascal.com`

## Drive
- No dedicated folder yet. File reports under the parent: `Agents Digital / Clients / Joe Rascal` (`14gHf6UZjgZ751CUP6iLz3Sf6WTTQBWSN`) or under `Joe Rascal Harley` until/unless a Joe Rascal Global subfolder is created.

## Drive subfolders
No dedicated Drive folder exists for Joe Rascal Global.

**Action required (two steps):**
1. Fix the Joe Rascal parent folder ID (see `joe-rascal.md` — scan returned Bad Request).
2. Create a `Joe Rascal Global` subfolder inside the Joe Rascal parent folder.
3. Update this brief with the new folder ID and run `scan-client-folders` to capture its subfolders.

Until resolved, all Joe Rascal Global reports fall back to `GOOGLE_DRIVE_REPORTS_FOLDER_ID`.

## Monday
- No dedicated board. Lives under the Joe Rascal parent board (`5026853960`).

## Notes
- This is the global storefront sibling to the Australian Harley/Ducati brands. The GA4 property lives under the Joe Rascal Harley account in GA4 Admin.
- When invoking `create_combined_seo_report`, pass `properties/525910399` explicitly — relying on `client_name` alone would route through Harley's property.
