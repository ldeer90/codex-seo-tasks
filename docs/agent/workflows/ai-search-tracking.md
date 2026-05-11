# AI Search Tracking

Set up and maintain SE Ranking AI Result Tracker prompts for client visibility in AI search surfaces.

## Use When

- The user asks about AI visibility, AI overviews, ChatGPT/Gemini/Perplexity tracking, prompt tracking, or AI search monitoring.

## Required Inputs

- Client sidecar and brief.
- SE Ranking project ID.
- Brand name and competitor/entity context.
- Confirmed market and engine scope.

## Phase 0 - Access And Input Preflight

- Memory: follow `docs/agent/client-memory.md`; read the client brief, sidecar when present, and timeline before workflow-specific sources, then append the client timeline with the proof summary or blocker.
- Confirm client sidecar/brief, canonical brand spelling, SE Ranking project, market scope, and existing AI tracker state.
- Confirm prompt/engine capacity and write intent before creating brands, engines, groups, or prompts.

### Missing-input routing

Route missing client setup, SE Ranking project, or brand/entity context to `ld-seo-client-onboarding`; SE Ranking access/capacity blockers to `ld-seo-maintenance`; strategy or prompt-priority uncertainty to `seo-roadmap-prioritisation.md`.

## Process

1. Validate client state.
2. Check existing AI brand, engines, prompt groups, and prompts.
3. Create or update brand only after confirming the canonical brand spelling.
4. Add engines only for confirmed markets.
5. Use Codex judgement to create prompt sets that reflect buyer questions, comparison questions, category research, and brand/entity questions.
6. Group prompts by intent and avoid duplicates.
7. Save prompt IDs/counts to the sidecar or proof block.

## Quality Gate

- Do not add prompts that are vague, impossible to evaluate, or irrelevant to the client's commercial reality.
- Check current prompt capacity before adding.
- Read back prompt groups/prompts after writes.

## Proof Block

Report engines, prompt groups, prompts added or updated, market scope, capacity, warnings, next review date, and client timeline update status.
