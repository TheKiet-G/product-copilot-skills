# Product Copilot Adapter

Use the modular skills in `skills/`. For product tasks, first invoke `product-core` to recall durable project context, then invoke exactly the task skill needed: `analyze-requirement`, `write-ticket`, `write-prd`, `draw-sequence`, `trace-artifacts`, `sync-knowledge`, `query-marketing-solution`, or `grilling`.

Treat Git-backed files under `knowledge/` as durable memory, not chat history. Load only retrieved context. Never auto-change templates, policies, business rules, or skill instructions; create a proposal.

Before drafting an artifact, detect material ambiguity using `skills/product-core/references/clarification-policy.md`. Ask the smallest set of blocking questions in Vietnamese and wait for the answers. Do not invent missing business behavior. Default all user-facing output to Vietnamese while preserving English technical terms.
