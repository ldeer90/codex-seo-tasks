# Shop Rongrong

## Routing
- `client_name`: `Shop Rongrong`
- Analytics subject: `seo@agents.digital` (source: `client` in `config/site-access.json`)
- Output subject: `hello@agents.digital`

## GA4
- Account: Shop Ronrong
- Property: Shop Rongrong - GA4
- Property ID: `properties/354478921`
- Web stream: `http://shoprongrong.com` (measurement ID `G-ZL24MRZEM7`)

## Web
- Primary URL: `https://www.shoprongrong.com`
- GA4 stream URL: `http://shoprongrong.com`
- Crawling/reporting note: use `https://www.shoprongrong.com` for `website_url` regardless of how it is stored in GA4.

## Drive
- Folder: `Agents Digital / Clients / Shop Rongrong`
- Folder ID: `1TTxwqCl5JurXCyva9kGK9rz5v66YzaXU`
- Visible to both `seo@` and `hello@`.

## Drive subfolders
Scanned 2026-05-11 via Google Drive MCP.

| Subfolder | ID |
|---|---|
| 00 Proposals | `15kCtGdaBurlGgoIaHxJuzS2g0_UpWFAQ` |
| 01 Onboarding | `1oq-xtRYs4sTVEA7sqR-98OxGSEYO4nOo` |
| 02 Roadmap | `1lz0rHHMYtbwwIDDxIX8TyWU3UJBhI5B7` |
| 03 Audits | `1ywpJIkNJddGRLdaGTiAnyDksoxP85pWD` |
| 04 Keyword Research | `17p1u8Al0K4OFdEZ0WZmcPlb6Yq_dIvKC` |
| 04 Keyword Research (duplicate/newer) | `1_6c6lFxotBjpuJgPWswFuaX5HLudSnxy` |
| 05 Content | `1OKlpQYetqto6mCJEjNQgeF3tlPbHtpvR` |
| 06 Links | `102otYWZ-W7vt-3y4NSKf8SCPsxV3oiaq` |
| 07 Reports | `1K66iztEtBye5mCowq-chwTkMr0E1uati` |
| 08 Invoices | `1JGYUytb3kJRqVMTq47WDnPpwR9xmSW_K` |

Filing targets:
- `create_combined_seo_report` → `07 Reports` (`1K66iztEtBye5mCowq-chwTkMr0E1uati`) until a nested SEO Reports folder is created.
- `create_firecrawl_seo_audit_doc` → `03 Audits` (`1ywpJIkNJddGRLdaGTiAnyDksoxP85pWD`)
- `create_site_audit_sheet` → `03 Audits` (`1ywpJIkNJddGRLdaGTiAnyDksoxP85pWD`)
- Collection content briefs → `05 Content` (`1OKlpQYetqto6mCJEjNQgeF3tlPbHtpvR`)

## SE Ranking
- Project ID: `11560829`
- Search engine: `1030519` (US market; live SE Ranking read on 2026-05-11 returned search_engine_id `200`, region_id `0`, lang `en`)
- Keywords tracked: 494 keyword-engine pairs after 2026-05-26 cleanup
- Check frequency: daily
- Note: Duplicate project `11619515` exists with 0 keywords — treat as inactive.

## Monday
- Workspace: Main workspace (`2556079`)
- Board: Shop Rongrong (`5026978284`) — 16 items, 3 groups, 5 columns
- Subitems board: Subitems of Shop Rongrong (`5026978497`)

## Notes
- Active client with monthly SEO work — the Monday board is one of the more populated ones.
- Market scope: US-based client. Use US keyword/volume assumptions for new SEO work.
- When running a combined report, use `https://www.shoprongrong.com` for `website_url` regardless of how it's stored in GA4 — the Firecrawl crawl needs the live HTTPS canonical.
- Operational sidecar: `docs/agent/clients/shop-rongrong.json`.
- Sidecar caveat: earlier onboarding used AU workflow defaults; refresh keyword volumes under the US market before new SE Ranking additions or content briefs.
- Crawl caveat: the 2026-05-11 five-page Firecrawl smoke test showed `robots: noindex, nofollow` metadata on some collection pages. Confirm indexability before briefing collection content.
