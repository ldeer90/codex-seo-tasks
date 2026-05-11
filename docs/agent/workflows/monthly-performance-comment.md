# Monthly Performance Comment

Create a concise client-ready monthly SEO performance comment for Monday. This is a read-first workflow:
ask for extra context at the beginning, present a detailed analysis in chat first, then write to Monday
only after the user has reviewed that analysis and explicitly approves posting.

Hard stop: do not create a Monday item, create a Monday update, or edit a Monday update before the
user has seen the detailed analysis in chat and replied with approval. Treat requests like "do this
client next" as permission to research and draft, not permission to post.

## Use When

- The user invokes `/ldseo-monthly-report <client>` and wants the reporting insight/comment workflow rather than a full Doc + Sheet.
- The user asks for a monthly SEO performance summary, insight comment, or Monday update.
- The user wants GA4, SE Ranking, Search Console, completed Monday work, and seasonality in one client-facing comment.
- The output is a short update, not a full Google Doc report.

## Required Inputs

- Client name.
- Reporting month and year.
- Report link, if one already exists.
- Monday item, if one already exists. If no item exists, ask before creating one unless the user explicitly asks you to create it.

## Phase 0 - Preflight

Follow `docs/agent/client-memory.md` for client memory.

1. Ask the user for any additional context before pulling or drafting:
   - client priorities or concerns
   - work completed outside Monday
   - campaign, stock, pricing, tracking, or website changes
   - report link or existing Monday item
   - whether they want a draft only or want to review before posting
2. Read `docs/agent/clients/<client>.md` for:
   - canonical client name
   - GA4 property
   - primary website URL
   - SE Ranking project and search engine
   - Monday board and current month group
3. Read `docs/agent/clients/<client>.json` when present and `docs/agent/clients/<client>-timeline.md` before pulling data. Use prior timeline entries to understand recent decisions, caveats, deliverables, and next actions.
4. Confirm Search Console access:
   - Prefer native Search Console API with the delegated analytics subject.
   - Use SE Ranking `PROJECT_getGoogleSearchConsole` only when native GSC is unavailable or the user asks for that source.
5. Confirm the posting rule: default is **draft in chat first** and do not post until the user gives explicit permission.

## Data Scope Rules

- GA4 must focus only on SEO-impactable channels:
  - `Organic Search`
  - `Organic Shopping`
- Exclude pages that SEO cannot reasonably impact:
  - `(not set)`
  - cart, checkout, account, order, payment, search, login, app, challenge, password, policy pages
- Use purchases and revenue only where ecommerce tracking is available.
- Do not include paid, direct, referral, email, social, or total-site metrics unless the user explicitly asks.

## Required Comparisons

Always include YoY. For a monthly report, pull at minimum:

- Current month.
- Previous month.
- Same month previous year.

Use these to explain:

- month-on-month movement
- year-on-year movement
- whether a dip is concerning or seasonal

When useful, also pull:

- previous quarter or year-to-date context
- event lead-up windows, such as Easter, Mother's Day, Father's Day, Christmas, Black Friday/Cyber Monday

## Seasonality

Always consider seasonality before writing conclusions.

1. Identify relevant calendar events for the client and category.
2. Use exact dates, not vague language:
   - example: "Easter Sunday was 5 April 2026, compared with 20 April 2025."
3. Compare equivalent event lead-up windows where possible:
   - Easter: 4 weeks ending Easter Sunday.
   - Mother's Day: 4 weeks ending Mother's Day.
   - Christmas: November and December, with December called out separately when needed.
4. Explain timing effects clearly:
   - "Demand was pulled into March and early April."
   - "April was a lead-up month for Mother's Day demand."

## GA4 Pull

For each relevant date range, gather:

- sessions
- users
- engaged sessions
- ecommerce purchases
- total revenue
- purchase rate
- AOV
- Organic Search vs Organic Shopping split
- top SEO-impactable landing pages by revenue and sessions
- seasonal page groups where relevant, such as `mother`, `mum`, `easter`, `birthday`, `get-well`, `care-package`

Report only the metrics that support the client-facing insight. Save raw exports to `/tmp/<client>-ga4-<period>.json` when large.

## SE Ranking Pull

Use the client brief SE Ranking project and search engine.

Gather:

- check dates for the reporting period
- visibility percent start and end
- average position start and end
- top 10 keyword count/share start and end
- keyword position changes from first check date to last check date
- domain overview history for broader YoY organic visibility context when useful

Prefer positive and strategically useful keyword examples. Include watchouts only when meaningful.

## Search Console Pull

Use native GSC `searchanalytics.query` where available.

Gather:

- top non-brand queries
- top pages
- query-page rows for relevant seasonal or commercial terms
- exact queries named in the report or current content focus

For each retained query/page, keep:

- impressions
- clicks
- CTR
- average position
- page URL

Use GSC to validate whether pages are visible for high-intent shopping queries, not just whether rankings exist in SE Ranking.

## Monday Work Pull

Read the client Monday board and reporting month group.

List completed tasks only:

- include task name
- include content type and topic for content tasks
- include broad activity type for links, such as "link building completed"
- do not include link destination information by default

If a task was created outside the month group but completed during the month and is clearly part of that month's work, mention it separately only if it matters.

## Analysis Shape

Always present a detailed analysis in chat before any client-facing Monday write. The chat analysis
must include the evidence needed for review: key GA4 numbers, comparison context, seasonality,
ranking movement, Search Console availability/results, notable landing pages, completed-work context
when relevant, caveats, and a proposed Monday-ready summary.

Draft the analysis in this order:

1. Executive summary at the top.
2. GA4 performance with YoY first, MoM second.
3. Seasonality explanation.
4. SE Ranking movement.
5. Search Console opportunity or validation.
6. Completed SEO work.
7. Final recommendation/watchout.

Keep the eventual Monday comment short. The chat analysis can be longer and should be detailed enough
for the user to review, challenge, or request edits before posting.

## Client-Ready Tone

- Lead with what matters.
- Avoid internal process language.
- Avoid over-explaining tools.
- Use "organic search and shopping" or "SEO-impactable organic performance" rather than "all traffic".
- Say "no major concerns" only when the data supports it.
- If a decline is seasonal, explain why with dates and supporting data.

## Monday Formatting

Use compact HTML optimised for Monday updates. Monday can create very large vertical gaps when
tables are placed after closed paragraph blocks, so do **not** wrap report updates in `<p>` tags.
Use headings plus `<br>` line breaks only, and place tables immediately after the heading or the
short intro sentence that introduces them.

Preferred format:

```html
<strong>April SEO Summary</strong><br>
Report link: <a href="https://example.com">View report</a><br><br>
<strong>Summary</strong><br>
Short paragraph.<br><br>
<strong>Keyword visibility</strong><br>
One short intro sentence.<br>
<table><tr><th>Keyword</th><th>Start</th><th>End</th><th>Movement</th><th>Notes</th></tr><tr><td>keyword</td><td>3</td><td>2</td><td>+1</td><td>Short note.</td></tr></table><br>
<strong>Recommended next focus</strong><br>
Final paragraph.
```

For keyword movement, use real `<table>` markup only when the user asks for tables or the update
needs more than 3 examples. Keep table cells short and avoid blank lines before or after the table.
Keyword tables in Monday updates must be quantified and client-friendly, not broad qualitative
grouping tables. Avoid tables shaped like `Keyword group | April result | Why it matters` unless the
user specifically asks for a strategic summary only. Do not include internal source columns such as
`Source` unless the source distinction is genuinely useful to the client. Prefer columns such as
keyword/query, monthly searches, start rank, end rank, movement, clicks, impressions, CTR, average
position, and a short plain-English client note. When the user asks for SE Ranking keyword changes,
use one compact table focused on rank movement rather than adding a separate GSC table. Include 1-3
balanced watch or downward rows when the data supports them, labelled plainly as watch, softening,
volatility, or opportunity rather than hiding them.

Avoid by default:

- `<p>` wrappers around the whole update
- placing a `<table>` immediately after `</p>`
- blank lines inside the HTML body
- more than one `<br><br>` between sections
- Markdown tables
- pipe tables
- `<ul>` / `<li>` blocks, unless the user confirms spacing is acceptable
- long raw URL lists
- duplicating completed-work lists when the same tasks are already visible on the Monday board or
  the attached report, unless the user explicitly asks for that section
- report proof blocks inside the client-facing comment

## Write Rules

- Always ask permission before posting to Monday. Do this even if the user previously asked for a report, even if a Monday item already exists, and even if the draft looks final.
- Present the detailed analysis and the proposed Monday-ready wording in chat first.
- Do not create or update Monday until the user explicitly approves posting after seeing the chat analysis.
- If the user asks for another client, run the analysis and stop at the review draft unless they explicitly approve the posted wording.
- If the user approves and an item exists, edit or add one update there.
- If no item exists, ask before creating one unless the user explicitly told you to create it.
- After writing, report the Monday item URL and update ID.

## Proof Block For The User

After completing the workflow, tell the user:

- client
- reporting period
- GA4 property and channels used
- SE Ranking project/search engine
- Search Console property/source
- Monday item/update URL if posted
- any caveats

Append the client timeline with the reporting period, GA4/GSC/SE Ranking/Monday sources, draft-only or posted status, Monday item/update URL if posted, caveats, and next focus. Do not include timeline/proof-block language in the client-facing Monday comment.
