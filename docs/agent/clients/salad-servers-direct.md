# Salad Servers Direct

## Routing
- `client_name`: `Salad Servers Direct` (also matches `salad servers` in fallback search)
- Analytics subject: `seo@agents.digital` (source: `client`)
- Output subject: `hello@agents.digital`

## GA4
- Account: Salad Servers Direct
- Property: Salad Servers Direct - GA4
- Property ID: `properties/378662387`
- Web stream: `https://direct.saladservers.com.au/` (measurement ID `G-1QXVMW31CK`)

## Web
- Primary URL: `https://direct.saladservers.com.au`
- Note the subdomain: `direct.saladservers.com.au`, not the apex.

## Drive
- Folder: `Agents Digital / Clients / Salad Servers`
- Folder ID: `1VTJy6FaSqLkOyRxaf7ZiAQuoIQVXatyf`

## Drive subfolders
Scanned 2026-05-08. Subject: `hello@agents.digital`.

| Subfolder | ID |
|---|---|
| 03 Audits | `1JIyzafg5Q49ExzvJMqCR-Bsu1Hm16N9o` |
| 04 Keyword Research / Meta-data (variant name) | `1KAg-cobu8wSxFGDeT-nyw3mIQQYXWS0e` |
| 07 Reports | `1RrX29zwEAiEv-SJFiqfSfkZAqJuKa6Sp` |
| 07 Reports / SEO Reports | ⚠ pending — create inside `07 Reports` then update this ID |
| 07 Reports / Benchmarks | ⚠ pending — create inside `07 Reports` then update this ID |
| 09 Website Plan (extra, not in template) | `1r85FjJqwEW3NA5fIcnLBHHAQtrJDy05x` |

Filing targets:
- `create_combined_seo_report` → `07 Reports / SEO Reports` (pending creation)
- `create_firecrawl_seo_audit_doc` → `03 Audits` (`1JIyzafg5Q49ExzvJMqCR-Bsu1Hm16N9o`)
- `create_site_audit_sheet` → `03 Audits` (`1JIyzafg5Q49ExzvJMqCR-Bsu1Hm16N9o`)

Until `SEO Reports` is created, `create_combined_seo_report` falls back to `GOOGLE_DRIVE_REPORTS_FOLDER_ID`.

## SE Ranking
- Project ID: `11273891`
- Keywords tracked: 198
- Check frequency: daily

## Monday
- Workspace: Main workspace
- Board: Salad Servers (`5025899615`) — 14 items, 2 groups, 6 columns
- Subitems: `5026186217`

## Notes
- The Drive folder is named "Salad Servers" but the GA4 client name is "Salad Servers Direct". The router handles both because the `client_name` lookup is case- and whitespace-insensitive, but pass `Salad Servers Direct` explicitly to be safe.
