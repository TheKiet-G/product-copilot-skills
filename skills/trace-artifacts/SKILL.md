---
name: trace-artifacts
description: Check consistency and traceability across product tickets, PRDs, acceptance criteria, and Mermaid sequence diagrams. Use when reviewing multiple product artifacts, detecting contradictions or omissions, assessing change impact, or preparing artifacts for implementation handoff.
---

# Trace Artifacts

1. Identify artifact metadata and project.
2. Extract requirement IDs, acceptance criteria, actors, interactions, business rules, assumptions, and failure paths.
3. Build a matrix with one row per requirement and columns for Ticket, PRD, Diagram, and status.
4. Mark each row `covered`, `partial`, `missing`, or `conflict`.
5. Report contradictions before omissions; cite exact headings or requirement IDs.
6. Check that every diagram interaction is authorized by a requirement and every behavioral requirement has an acceptance test.
7. Distinguish source conflict from harmless wording differences.
8. If authoritative intent cannot be determined, ask the user a focused question in Vietnamese instead of selecting a winner.
9. Recommend the smallest source-of-truth correction; never silently rewrite governed artifacts.

Read [references/traceability-rules.md](references/traceability-rules.md) for severity and pass criteria.
