# TravelKon

## Routing
- `client_name`: `TravelKon`
- Analytics subject: `seo@agents.digital` (source: `client`)
- Output subject: `hello@agents.digital`

## GA4
TravelKon has two GA4 properties — pick deliberately:

| Use case | Property | ID |
|---|---|---|
| Web/SEO reporting (default) | TravelKon - GA4 | `properties/387124003` |
| App + cross-platform notifications | travelkon-app-notification | `properties/532415351` |

- Web stream (`387124003`): `https://www.travelkon.com.au` — `G-NKF7LKLVW5`
- App+web property (`532415351`) streams: `TravelKon` (`G-ZE1BR9QTCD`), `Travelkon Android`, `Travelkon iOS`

For SEO work always use `properties/387124003`. Switch to `532415351` only when the user explicitly asks about app analytics.

## Web
- Primary URL: `https://www.travelkon.com.au`

## Drive
- Folder: `Agents Digital / Clients / TravelKon`
- Folder ID: `175zcM_g56_jtpU1m9bzAMFvLFahXAqS3`

## Drive subfolders
Scanned 2026-05-08. Subject: `hello@agents.digital`.

| Subfolder | ID |
|---|---|
| 03 Audits | `1aEbqpVIWbkaz8dkMZGKa14v6b5iJn_Jb` |
| 07 Reports | `1HCuM9DP0xZ9sjms8Y6C1AZhgWap_A5pr` |
| 07 Reports / SEO Reports | ⚠ pending — create inside `07 Reports` then update this ID |
| 07 Reports / Benchmarks | ⚠ pending — create inside `07 Reports` then update this ID |

Filing targets:
- `create_combined_seo_report` → `07 Reports / SEO Reports` (pending creation)
- `create_firecrawl_seo_audit_doc` → `03 Audits` (`1aEbqpVIWbkaz8dkMZGKa14v6b5iJn_Jb`)
- `create_site_audit_sheet` → `03 Audits` (`1aEbqpVIWbkaz8dkMZGKa14v6b5iJn_Jb`)

Until `SEO Reports` is created, `create_combined_seo_report` falls back to `GOOGLE_DRIVE_REPORTS_FOLDER_ID`.

## SE Ranking
- Project ID: `11580098`
- Keywords tracked: 113
- Check frequency: daily

## Monday
- Workspace: Main workspace
- Board: TravelKon (`5026863900`) — 9 items, 2 groups, 6 columns
- Subitems: `5026863958`

## Notes
- If the user just says "TravelKon" without a property qualifier, default to the web property (`387124003`) and confirm.
