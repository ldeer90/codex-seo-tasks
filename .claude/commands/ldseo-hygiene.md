---
description: Audit SE Ranking projects, find duplicates, manage plan cap (2,000 pairs)
argument-hint: [client or "all"]
---

# LD SEO — SE Ranking Hygiene

Review and clean up SE Ranking projects across all clients. Run before any keyword-addition work to avoid hitting the plan cap, or when the cap blocks an add.

## MCPs / APIs used

| Service | Tools / endpoints |
|---|---|
| **SE Ranking Project API** | `PROJECT_listProjects`, `PROJECT_listKeywords`, `PROJECT_deleteKeywords` (only after user confirmation), `PROJECT_listSubAccounts` |
| **SE Ranking Data API** | `DATA_getCreditBalance`, `DATA_getSubscription` (plan capacity check) |
| **Local scripts** | `sync_collection_sidecar_from_exports.py` (after deletions, re-sync affected client sidecars) |

## How to invoke

```
/ldseo-hygiene [client or "all"]
```

Examples:

```
/ldseo-hygiene
/ldseo-hygiene all
/ldseo-hygiene melani-the-label
```

If no argument, audit across all projects.

## When to run

- Before adding keywords to any project
- When the plan cap error appears (`available limit of adding is N`)
- Monthly health check

## Required reading

`docs/agent/workflows/se-ranking-hygiene.md`

## Plan model

- `keyword_count` from `PROJECT_listProjects` reflects **keyword-engine pairs**, not unique keywords. AU + US tracking = 2 pairs per keyword.
- Plan cap: **2,000 pairs** total across all projects
- Most clients are AU-only (1 engine per keyword). Melani is AU+US (2 engines per keyword).

## Steps

### Step 1 — Project-level audit

```
PROJECT_listProjects()
```

Note `id`, `title`, `keyword_count` per project. Sum to get current pair usage. Flag duplicate domains.

### Step 2 — Identify duplicates

Within and across projects. Duplicate keyword-engine pairs are wasted plan capacity.

### Step 3 — Identify cleanup candidates

- Inactive keywords (no rank movement in 90+ days)
- Keywords below the agreed difficulty/volume threshold
- Test keywords left over from setup

### Step 4 — Recommend or execute deletions

Confirm with user before deleting. Each deleted pair frees 1 from the plan cap.

## Hard rules

- Never delete keywords without user confirmation
- Document deletions in the affected client's sidecar `qa.se_ranking_changes`
- After deletions, re-export `PROJECT_listKeywords` for affected clients and re-sync sidecars
