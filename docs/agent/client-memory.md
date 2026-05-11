# Client Memory Timeline

Client memory is the chronological record of what the agent learned, changed, created, or decided for a client. It complements the client brief and JSON sidecar:

- Client brief (`docs/agent/clients/<client-slug>.md`) = human-readable source of truth for routing, access, folders, boards, and caveats.
- Client sidecar (`docs/agent/clients/<client-slug>.json`) = structured operational state for workflows, validators, collection data, and output IDs.
- Client timeline (`docs/agent/clients/<client-slug>-timeline.md`) = chronological memory of task runs, decisions, caveats, proof summaries, and next actions.

## Required Path

Every active client must have:

```text
docs/agent/clients/<client-slug>-timeline.md
```

Use the same slug as the client brief and sidecar.

## Required Preflight Read Order

For every client-scoped LD SEO task, including ad hoc requests:

1. Read `docs/agent/clients/<client-slug>.md`.
2. Read `docs/agent/clients/<client-slug>.json` when it exists.
3. Read `docs/agent/clients/<client-slug>-timeline.md`.
4. Read the routed skill and workflow docs.
5. Read workflow-specific sources such as Drive folders, Monday board schema, GA4/GSC/SE Ranking exports, or cached crawl files.

If a timeline is missing:

- For a newly onboarded client, create it during onboarding from `CLIENT_TIMELINE_TEMPLATE.md`.
- For a legacy client, create a baseline entry from existing brief/sidecar/deliverable facts only.
- Do not reconstruct history from chat memory or assumptions.

## Required Timeline Entry

Append one entry after every successful client-scoped task and after any stopped task that discovers a blocker worth remembering.

Each entry must include:

| Field | Requirement |
|---|---|
| `Date` | ISO date, local workspace date. |
| `Task` | Workflow or ad hoc task name. |
| `Request / source` | User request, command, or triggering context. |
| `Evidence checked` | Brief, sidecar, timeline, APIs, exports, Drive, Monday, or validator sources checked. |
| `Outputs` | Docs, Sheets, files, Monday items/updates, changed sidecar fields, or `None`. |
| `Decisions` | Business, SEO, routing, or content decisions made. |
| `Caveats` | Warnings, blockers, stale data, missing access, or explicit limitations. |
| `Next action` | The next useful step or `None`. |
| `Proof summary` | Short summary of validation/readback/proof block outcome. |

Keep entries concise. Client timelines are for future agents to regain context quickly, not for raw API dumps.

## Client-Facing Boundary

Do not paste timeline entries, proof blocks, local paths, or validator labels into client-facing Docs, Sheets, or Monday comments. Summarise only the client-safe insight when needed.
