---
name: product-core
description: Maintain portable, durable product context in a Git-backed Markdown knowledge base. Use when an agent needs to ingest project documents, recall prior decisions or terminology across chats and clients, add safe sourced facts, propose governed knowledge changes, enforce token budgets, or prepare context for product artifacts.
---

# Product Core

Use the repository root as the source of truth. Never treat chat history as durable memory.

## Workflow

1. Identify the project. If it is unknown, list `knowledge/projects/` and ask only when multiple projects are plausible.
2. Run `python3 skills/product-core/scripts/product_memory.py recall --project <id> --query "<task>"`.
3. Use the returned compact context. Read a cited source document only when the compact context is insufficient.
4. Check whether the input is sufficient. If a material ambiguity remains, ask clarification questions in Vietnamese and wait for the answers.
5. Perform the requested product workflow only after blocking questions are resolved or the user explicitly authorizes documented assumptions.
6. Extract only durable, source-backed learning. Add low-risk facts with `learn`; send policy, template, business-rule, conflicting, or instruction changes to `propose`.
7. Never store credentials, personal secrets, or confidential content without an explicit repository policy.

## Commands

```bash
python3 skills/product-core/scripts/product_memory.py init-project --project payments
python3 skills/product-core/scripts/product_memory.py ingest --project payments --source docs/spec.pdf
python3 skills/product-core/scripts/product_memory.py recall --project payments --query "refund timeout" --budget 1800
python3 skills/product-core/scripts/product_memory.py learn --project payments --kind glossary --statement "MOTO means mail order/telephone order." --source docs/terms.md
python3 skills/product-core/scripts/product_memory.py propose --project payments --kind business-rule --statement "Refunds expire after 30 days." --source ticket-123
```

Use `--scope global` only for knowledge that applies to every project.

## Memory Rules

- Store atomic facts with `id`, `kind`, `statement`, `source`, `updated_at`, `confidence`, and `status`.
- Prefer `active`; mark superseded knowledge `deprecated` instead of deleting it.
- Do not add a fact when an active fact with the same normalized statement exists.
- Do not automatically resolve conflicts. Create a proposal and surface both claims.
- Treat glossary entries, explicit system facts, source links, and non-sensitive preferences as low risk.
- Treat policies, templates, business rules, agent instructions, and conflict resolution as governed.

Read [references/memory-policy.md](references/memory-policy.md) before changing knowledge.
Read [references/retrieval-policy.md](references/retrieval-policy.md) when tuning context selection.
Read [references/clarification-policy.md](references/clarification-policy.md) before asking the user for missing information.
