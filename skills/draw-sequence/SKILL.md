---
name: draw-sequence
description: Create and validate Mermaid sequence diagrams that trace to product requirements. Use when visualizing an API, service, user, event, integration, happy path, alternative path, retry, timeout, or error interaction as a sequence diagram.
---

# Draw Sequence

1. Recall only actors, systems, requirements, APIs, and failure behavior relevant to the flow.
2. Apply `product-core/references/clarification-policy.md`. Ask in Vietnamese when actors, trigger, ordering, sync/async behavior, response, timeout, retry, or error handling is materially unclear.
3. Wait for blocking answers; list only explicitly authorized assumptions.
4. Use Mermaid `sequenceDiagram` as the source of truth.
5. Include `autonumber`, stable requirement references in notes, and meaningful participant aliases.
6. Model the happy path plus known alternative, timeout, retry, and error paths with `alt`, `opt`, `loop`, or `break`.
7. Do not invent endpoints, status codes, queues, or retry policy.
8. Save as Markdown and validate with `validate-artifact --type sequence --file <path>`.
9. Trace the diagram to the ticket/PRD when available.

Read [references/mermaid-standard.md](references/mermaid-standard.md) for syntax and review rules.
