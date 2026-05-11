# Acorn Rentals

## Routing
- `client_name`: `Acorn Rentals`
- Analytics subject: `hello@agents.digital` (source: `client` — explicitly mapped because `seo@` cannot read this property)
- Output subject: `hello@agents.digital`

This is one of the two clients (along with Agents Digital) where the analytics subject is `hello@`, not `seo@`. Confirm via `resolve_google_access_subject` if there's any doubt.

## GA4
- Account: Acorn Rentals
- Property: Acorn Rentals - GA4
- Property ID: `properties/423383715`
- Web stream: `Acorn Rentals - GA4` — `http://www.acornrentals.com.au/` (measurement ID `G-V0TFMZMDWN`)

## Web
- Primary URL: `https://www.acornrentals.com.au`
- GA4 stream is HTTP — verify the live canonical before crawling. Most modern sites redirect to HTTPS.

## Drive
- Folder: `Agents Digital / Clients / Acorn Rentals`
- Folder ID: `1M2MXfkRFsAMy5nFoM2m7miNOnjBEkvoj`

## Drive subfolders
Scanned 2026-05-08. Subject: `hello@agents.digital`.

| Subfolder | ID |
|---|---|
| 03 Audits | `1ZGPxHEygUPhes-0twOuoTkDBygIW-tAs` |
| 07 Reports | `1gupoXp_cjGHm3ixSEIs3PFpKTb2ataJ2` |
| 07 Reports / SEO Reports | ⚠ pending — create inside `07 Reports` then update this ID |
| 07 Reports / Benchmarks | ⚠ pending — create inside `07 Reports` then update this ID |

Filing targets:
- `create_combined_seo_report` → `07 Reports / SEO Reports` (pending creation)
- `create_firecrawl_seo_audit_doc` → `03 Audits` (`1ZGPxHEygUPhes-0twOuoTkDBygIW-tAs`)
- `create_site_audit_sheet` → `03 Audits` (`1ZGPxHEygUPhes-0twOuoTkDBygIW-tAs`)

Until `SEO Reports` is created, `create_combined_seo_report` falls back to `GOOGLE_DRIVE_REPORTS_FOLDER_ID`.

## SE Ranking
- Project ID: `11444792`
- Keywords tracked: 26
- Check frequency: daily
- Note: Low keyword count — worth expanding with the client's target terms.

## Monday
- Workspace: Main workspace
- Board: Acorn Car Rentals (`5026665037`) — 30 items, 6 groups, 7 columns
  - Note the board name is "Acorn Car Rentals" while the GA4 client name is "Acorn Rentals". Use the board ID, not the name.
- Subitems: `5026665038`

## Notes
- Highest-volume Monday board after Joe Rascal Harley (30 items).
- If a tool call returns a 401/403 from GA4 for this property, the most likely cause is `seo@` being routed by mistake. Re-run `resolve_google_access_subject` with `validate_ga4_access=True` and confirm the `analytics.subject` is `hello@agents.digital`.
