# Full-Site Audit

Crawl a site (or section), analyse the crawl dataset, and save client-ready evidence in the client's audit folder.

Default to Screaming Frog for technical full-site audits when the local CLI and project-approved config are available. Use Firecrawl only for lightweight content/page checks, quick proof-of-reachability, or when Screaming Frog is unavailable.

## Phase 0 - Access And Input Preflight

Memory: follow `docs/agent/client-memory.md`; read the client brief, sidecar when present, and timeline before workflow-specific sources, then append the client timeline with the proof summary or blocker.

1. Open the client brief; confirm `client_name` and `start_url`.
2. Validate the client sidecar with `python3 scripts/validate_client_json.py --client-json docs/agent/clients/<client>.json`.
3. Confirm crawler:
   - Screaming Frog CLI path: `/Applications/Screaming Frog SEO Spider.app/Contents/MacOS/ScreamingFrogSEOSpiderLauncher`.
   - Shopify config: `Codex Shopify Standard SEO Spider Config.seospiderconfig`.
   - Drive destination: client sidecar `drive.folders.03_audits`.
4. Confirm crawl scope and storage:
   - Start from the canonical homepage unless the user asks for a section.
   - Use the config's crawl limits and robots settings; do not bypass robots.txt.
   - Confirm before uploading a raw export zip to Drive.
5. For Firecrawl fallback only, confirm crawl limit. Default 25. Hard ceiling 100. For a typical SME site, 50 covers most of the indexable surface.

### Missing-input routing

Route missing client setup, Drive folder, or website URL to `ld-seo-client-onboarding`; Screaming Frog, Firecrawl, access, or Drive filing blockers to `ld-seo-maintenance`; strategic follow-up recommendations to `seo-roadmap-prioritisation.md` after the audit is validated.

## Run - Screaming Frog

Dry-run the command first when changing scope:

```bash
python3 scripts/run_screaming_frog_audit.py \
  --client-json docs/agent/clients/<client>.json \
  --start-url https://example.com \
  --dry-run
```

Run and save the zipped raw export to the client's `03 Audits` folder after confirmation:

```bash
python3 scripts/run_screaming_frog_audit.py \
  --client-json docs/agent/clients/<client>.json \
  --start-url https://example.com \
  --upload-to-drive
```

The runner uses the saved Shopify `.seospiderconfig`, exports CSV tabs, saves Screaming Frog reports, writes `analysis-summary.json`, `analysis-summary.md`, and `manifest.json`, then uploads a zip of the export folder when `--upload-to-drive` is present.

## Run - Firecrawl Fallback

Use only when Screaming Frog is unavailable or the user explicitly wants the existing lightweight report:

```json
{
  "client_name": "<from brief>",
  "start_url": "https://example.com",
  "limit": 50
}
```

Tool: `create_firecrawl_seo_audit_doc`.

## Verify

- Screaming Frog export folder contains CSV exports, reports, logs, `analysis-summary.json`, `analysis-summary.md`, and `manifest.json`.
- Drive upload URL opens from the client `03 Audits` folder.
- Export row counts match expectation for the site and config; call out if the crawl was blocked, truncated, or mostly non-indexable utility URLs.
- For Firecrawl fallback, `pages_audited` matches expectation, and `google_subjects.output.subject` is the expected output owner.
- Read back or inspect created Drive outputs before calling the audit client-ready.

## Client-Presentable QA

Use Codex judgement to turn raw crawl rows into useful agency output:

- Lead with the top issues by SEO/business impact, not only frequency.
- Include affected page examples and practical next actions.
- Separate quick wins from structural issues.
- Call out crawl limitations, blocked pages, thin samples, or low confidence.
- Confirm the Doc and Sheet are in the expected client folder or state the filing action still needed.

## Deliver

Reply with:

- Screaming Frog export zip URL, or Doc/Sheet URLs for Firecrawl fallback.
- Local export folder path.
- Internal rows/pages analysed.
- Top priority issues and next actions
- Remaining warnings or limitations

## Proof Block

Report client, start URL, crawler, config path, export folder, Drive folder/upload URL, output subject, internal rows/pages analysed, top issues, crawl limitations, and client timeline update status.

## When to use `crawl_site` instead

If the user only wants raw crawl data (no Drive output), call `crawl_site` and return the page count and a small sample of the `data` array. Don't dump the whole response into chat.
