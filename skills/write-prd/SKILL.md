---
name: write-prd
description: Draft and validate source-backed Product Requirement Documents in Vietnamese while preserving English technical terms. Use when creating, revising, reviewing, or expanding a PRD from tickets, discovery notes, system documentation, or project knowledge.
---

# Write PRD

1. Recall project context through `product-core`.
2. Apply `product-core/references/clarification-policy.md`. Ask blocking clarification questions in Vietnamese and wait for answers.
3. Check `template-status --type prd`.
4. If no approved template is installed, return **DRAFT — TEMPLATE REQUIRED**, identify missing decisions, and do not present the PRD as final.
5. Separate sourced facts, assumptions, open questions, and recommendations.
6. Cover the approved template exactly; do not invent business rules to fill gaps.
7. Add artifact metadata and stable requirement IDs (`REQ-001`, `REQ-002`, ...).
8. Validate with `validate-artifact --type prd --file <path>`.
9. Run `trace-artifacts` when a related ticket or diagram exists.

Read [references/prd-quality.md](references/prd-quality.md) before finalizing.
