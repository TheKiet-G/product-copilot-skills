---
name: sync-knowledge
description: Sync the Growth Enablement knowledge base against Confluence by comparing page versions with ingested chunks, then deprecating stale chunks and re-ingesting updated pages. Requires Atlassian MCP connected. Use when knowledge may be stale or after Confluence updates.
---

# Sync Knowledge

Requires an active Claude Code session with Atlassian Rovo MCP connected.

## Workflow

### Step 1 — Build ingested version map

Parse `knowledge/projects/growth-enablement/chunks.jsonl`. For every active chunk,
extract page ID and version from the `source` field pattern
`confluence://{SPACE}/pages/{PAGE_ID}?version={N}`.

Build a dict: `page_id → { max_version, space, title }`.
If a page appears multiple times (multiple chunks), keep the highest version seen.

### Step 2 — Walk live Confluence pages

For each space root, use MCP `getConfluencePageDescendants`:
- ZPPROM root: page ID `5964759`
- GP root: page ID `200804407` (GE branch — exclude RC siblings)

For each page returned, note `id`, `title`, `version.number`, `space.key`.

Apply the same exclusion filters as the original scan:
- Skip pages with "archive", "meeting note", "weekly report", "onboarding" (credential sections),
  or RC branches not explicitly requested.

### Step 3 — Diff

For each live page:
- `current_version <= ingested_version` → log "up-to-date", skip.
- Page ID not in map → new page, proceed to Step 4.
- `current_version > ingested_version` → changed, proceed to Step 4.

### Step 4 — Re-ingest changed or new pages

For each page to update:

**4a.** Fetch full content via MCP `getConfluencePage` with `body-format: storage` or `view`.

**4b.** If the page was previously ingested (exists in map), deprecate old chunks first:
```bash
python3 skills/product-core/scripts/product_memory.py deprecate-by-source \
  --project growth-enablement \
  --source-prefix "confluence://{SPACE}/pages/{PAGE_ID}"
```

**4c.** Ingest new content:
```bash
echo "<page body>" | python3 skills/product-core/scripts/product_memory.py ingest-text \
  --project growth-enablement \
  --source "confluence://{SPACE}/pages/{PAGE_ID}?version={N}" \
  --title "{PAGE_TITLE}"
```

Unchanged sections are deduped automatically by content hash — only truly changed
chunks are added.

### Step 5 — Report

Print a summary table:
- Pages checked / up-to-date / re-ingested / skipped (excluded) / errors
- Chunks deprecated / chunks added / chunks skipped (duplicate)
- Timestamp of sync

## Notes

- Never delete deprecated chunks. Deprecation is soft — old chunks remain in JSONL
  with `status: deprecated` and are excluded from recall automatically.
- Do not update `knowledge/projects/growth-enablement/index.md` automatically.
  Propose index changes via `product-core propose` if summary needs updating.
- If a page fetch fails (auth error, timeout), log the error and continue — do not
  abort the entire sync.
