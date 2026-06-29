---
name: analyze-requirement
description: Analyze product requirements for ambiguity, acceptance criteria, business rules, edge cases, dependencies, risks, and change impact. Use before drafting a ticket, PRD, or sequence diagram, or when reviewing whether a requirement is implementation-ready.
---

# Analyze Requirement

Recall relevant context with `product-core`, apply `product-core/references/clarification-policy.md`, then produce:

1. **Goal and users** — desired outcome and affected actors.
2. **Known facts** — each with a source.
3. **Assumptions** — explicit and testable.
4. **Clarifications** — only questions whose answers materially change behavior.
5. **Business rules and states** — including precedence and lifecycle.
6. **Acceptance criteria** — observable Given/When/Then scenarios.
7. **Edge and failure cases** — validation, permissions, concurrency, timeout, retry, partial failure, and recovery where relevant.
8. **Dependencies and risks** — systems, teams, data, compliance, rollout, and monitoring.
9. **Change impact** — affected APIs, events, storage, UI, operations, analytics, and existing artifacts.

When any clarification is blocking, ask the questions in Vietnamese and stop before generating a final Ticket, PRD, or Diagram. Continue only after the user answers or explicitly authorizes assumptions.

Classify readiness as `ready`, `ready-with-assumptions`, or `blocked`. Never convert an unsupported assumption into a fact.

Read [references/analysis-checklist.md](references/analysis-checklist.md) for the domain-neutral checklist.
