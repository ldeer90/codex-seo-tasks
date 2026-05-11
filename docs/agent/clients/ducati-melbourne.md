# Ducati Melbourne

## Routing
- `client_name`: `Ducati Melbourne`
- Analytics subject: `seo@agents.digital` (source: `client`)
- Output subject: `hello@agents.digital`
- Property is also visible to `hello@agents.digital`.

## GA4
- Account: Ducati Melbourne
- Property: Ducati Melbourne - GA4
- Property ID: `properties/402313624`
- Web streams on this property:
  - `Ducati Melbourne - GA4` — `https://www.ducatimelbourne.com.au/` (measurement ID `G-DNQVKWJJ0E`)
  - `Joe Rascal Ducati` — `https://joerascalducati.com.au/` (measurement ID `G-CFPVWFWNGJ`)

The Joe Rascal Ducati stream lives on the **Ducati Melbourne** property. When auditing the Joe Rascal Ducati site, still query `properties/402313624` — but pass `https://joerascalducati.com.au` as `website_url` so the right pages are scraped. There is no separate Joe Rascal Ducati GA4 property.

## Web
- Primary URL: `https://www.ducatimelbourne.com.au`

## Drive
- Folder: `Agents Digital / Clients / Joe Rascal Ducati` (the Ducati Melbourne work files under the Joe Rascal Ducati folder by current convention — confirm if creating new files)
- Folder ID: `157-ddATrb2byi0VMJYKg9JET4RzqIFFr`

## Drive subfolders
Scanned 2026-05-08. Subject: `hello@agents.digital`. Uses the `Joe Rascal Ducati` client folder by convention.

| Subfolder | ID |
|---|---|
| 03 Audits | `1zqzxqVT2aeJ1aahoGW3EM0qEoqomnB5x` |
| 07 Reports | `1dzj65zJm15qNxV0AK0VyefNsr1prGkd2` |
| 07 Reports / SEO Reports | ⚠ pending — create inside `07 Reports` then update this ID |
| 07 Reports / Benchmarks | ⚠ pending — create inside `07 Reports` then update this ID |

Filing targets:
- `create_combined_seo_report` → `07 Reports / SEO Reports` (pending creation)
- `create_firecrawl_seo_audit_doc` → `03 Audits` (`1zqzxqVT2aeJ1aahoGW3EM0qEoqomnB5x`)
- `create_site_audit_sheet` → `03 Audits` (`1zqzxqVT2aeJ1aahoGW3EM0qEoqomnB5x`)

Until `SEO Reports` is created, `create_combined_seo_report` falls back to `GOOGLE_DRIVE_REPORTS_FOLDER_ID`.

## SE Ranking
- Project ID: `10993280`
- Keywords tracked: 100
- Check frequency: daily
- Note: Project is titled "joerascalducati.com.au" — used for both Joe Rascal Ducati site work and Ducati Melbourne where they overlap.

## Monday
- Workspace: Main workspace
- Board: Joe Rascal Ducati (`5025418481`) — 25 items, 5 groups, 7 columns
- Subitems: `5025418482`

## Notes
- Closely tied to the Joe Rascal group — see `joe-rascal.md` for the parent context.
- The shared GA4 property for both `ducatimelbourne.com.au` and `joerascalducati.com.au` is the most common source of confusion. Confirm `website_url` with the user.
