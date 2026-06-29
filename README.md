# Product Copilot Skills

Portable, Git-backed product skills for Codex, Claude Code, Cursor, and other agent clients.

This repository turns a general coding/product assistant into a source-backed Product Copilot. It helps product teams read durable project knowledge, ask the right clarification questions, draft Jira tickets and PRDs, draw sequence diagrams, trace requirements across artifacts, and safely improve the shared knowledge base without depending on chat history.

The core idea is simple:

1. Store reusable product context in `knowledge/`.
2. Route every product task through small, explicit skills in `skills/`.
3. Keep business rules, templates, and policies governed through proposals instead of silently rewriting them.
4. Validate generated artifacts before handoff.

## What problem this solves

Product work often breaks because context lives in scattered chats, Confluence pages, Jira tickets, screenshots, or a single person's memory. A normal AI chat may answer well once, then forget the old context or silently invent missing business behavior.

This skill set is designed to solve that:

- Recall old source-backed context across sessions.
- Keep Confluence/Jira/project knowledge searchable through Git-backed Markdown/JSONL.
- Separate facts, assumptions, open questions, and proposed business rules.
- Produce Vietnamese product artifacts while preserving English technical terms.
- Standardize ticket, PRD, sequence, traceability, and requirement-review workflows.
- Avoid leaking tokens, API keys, local config, or private generated outputs into source control.

## Repository layout

```text
.
├── AGENTS.md                         # Codex adapter
├── CLAUDE.md                         # Claude Code adapter
├── .cursor/rules/product-copilot.mdc # Cursor adapter
├── config/product-copilot.json       # Safe learning / governed learning config
├── skills/                           # Modular Product Copilot skills
├── templates/                        # Ticket / PRD templates and template status
├── knowledge/                        # Git-backed memory framework
│   ├── global/                       # Optional global context skeleton
│   └── projects/_template/           # Empty project template
└── tests/                            # CLI regression tests
```

Generated outputs, private Confluence/Jira ingests, proposals, audit logs, and local secrets are intentionally ignored by `.gitignore`.

## Skill set

| Skill | Purpose | Use when |
|---|---|---|
| `product-core` | Durable memory layer: initialize project knowledge, ingest documents, recall relevant context, learn safe facts, propose governed changes, validate artifacts. | Any product task that needs source-backed context. This should run first. |
| `analyze-requirement` | Review a requirement for ambiguity, business rules, edge cases, dependencies, acceptance criteria, and readiness. | Before writing a ticket/PRD or when a requirement feels unclear. |
| `write-ticket` | Draft Jira-style ticket descriptions in Vietnamese with source metadata and acceptance criteria. | Creating or revising implementation-ready Jira tickets. |
| `write-prd` | Draft source-backed PRDs with stable requirement IDs and explicit assumptions/open questions. | Creating or expanding PRDs from docs, Figma, tickets, or discovery notes. |
| `draw-sequence` | Create Mermaid sequence diagrams for API/service/user/event flows. | Visualizing happy path, error path, retry, timeout, async interactions. |
| `trace-artifacts` | Check consistency across tickets, PRDs, acceptance criteria, and sequence diagrams. | Preparing artifacts for grooming, handoff, or implementation. |
| `sync-knowledge` | Compare ingested Confluence page versions against live Confluence and re-ingest changed pages. | After Confluence changes or when knowledge may be stale. Requires Atlassian MCP/connector. |
| `grilling` | Stress-test assumptions one by one before finalizing an artifact or decision. | You want a hard review before committing to a plan/PRD/ticket. |

## How the skills work together

For product tasks, the intended workflow is:

```text
User request
  ↓
product-core recall
  ↓
clarification policy
  ↓
exactly one task skill
  ↓
artifact validation / traceability
  ↓
safe learning or governed proposal
```

Example:

- For a Jira ticket: `product-core` → `write-ticket`
- For a PRD: `product-core` → `write-prd`
- For requirement review: `product-core` → `analyze-requirement`
- For sequence diagram: `product-core` → `draw-sequence`
- For cross-checking PRD/ticket/diagram: `product-core` → `trace-artifacts`

`product-core` is deliberately separated from drafting skills. It is responsible for memory and governance; task skills are responsible for one artifact type.

## Agent adapters

Different AI clients read different instruction files, but all adapters point to the same skill source:

- Codex reads `AGENTS.md`.
- Claude Code reads `CLAUDE.md`.
- Cursor reads `.cursor/rules/product-copilot.mdc`.
- Claude slash-style commands live in `.claude/commands/`.

The adapters intentionally stay thin. The source of truth is always `skills/*/SKILL.md`.

## Quick start

Install dependencies:

```bash
python3 -m pip install -r requirements.txt
```

Initialize a project memory space:

```bash
python3 skills/product-core/scripts/product_memory.py init-project \
  --project my-project
```

Ingest a local document:

```bash
python3 skills/product-core/scripts/product_memory.py ingest \
  --project my-project \
  --source path/to/document.md
```

Ingest exported Confluence text:

```bash
confluence-export-command | python3 skills/product-core/scripts/product_memory.py ingest-text \
  --project my-project \
  --source "confluence://SPACE/pages/PAGE_ID?version=N" \
  --title "Page title"
```

Recall relevant context:

```bash
python3 skills/product-core/scripts/product_memory.py recall \
  --project my-project \
  --query "budget alert validation for promotion campaigns" \
  --budget 12000 \
  --max-results 20
```

Validate an artifact:

```bash
python3 skills/product-core/scripts/product_memory.py validate-artifact \
  --type ticket \
  --file outputs/ticket-description/GE-123_example.md
```

## Memory and governance model

`product-core` supports two paths:

### Safe learning

Use `learn` for low-risk, source-backed facts:

- glossary terms;
- source links;
- explicit system facts;
- non-sensitive preferences;
- approved decisions.

Example:

```bash
python3 skills/product-core/scripts/product_memory.py learn \
  --project growth-enablement \
  --kind glossary \
  --statement "Promotion Code is a CRM campaign where a user enters a code to receive a configured reward if rules pass." \
  --source "confluence://GP/pages/333516693?version=75"
```

### Governed proposals

Use `propose` for anything that should not become truth automatically:

- business rules;
- policies;
- templates;
- agent instructions;
- conflict resolution;
- low-confidence inferred behavior.

Example:

```bash
python3 skills/product-core/scripts/product_memory.py propose \
  --project growth-enablement \
  --kind business-rule \
  --statement "Budget Alert threshold must be an integer from 1 to 99." \
  --source "confluence://GP/pages/329219233?version=74"
```

This creates a pending JSON proposal under `knowledge/proposals/` in the working tree. In this source repository, project-specific proposals are ignored by default because they often contain internal project context.

## Artifact templates

Templates live under `templates/`.

Ticket template status is configured in:

```text
templates/ticket/template.json
```

PRD template status is configured in:

```text
templates/prd/template.json
```

Install an approved template:

```bash
python3 skills/product-core/scripts/product_memory.py install-template \
  --type ticket \
  --file templates/ticket/change-request-template.md \
  --version 2026-06-16 \
  --heading "Context" \
  --heading "Requirement" \
  --heading "Acceptance Criteria"
```

Until a template is installed, the corresponding artifact validation intentionally fails. This is by design: the assistant must not present an artifact as final when the approved template is missing.

## Confluence and Jira usage

This repository does not store credentials.

Use a local MCP connector, browser session, or export command to fetch Confluence/Jira content, then ingest the sanitized page body through `product_memory.py`.

Recommended source format:

```text
confluence://SPACE/pages/PAGE_ID?version=N
jira://PROJECT/ISSUE-ID
figma://FILE_ID/node/NODE_ID
```

When syncing Confluence through `sync-knowledge`, keep these rules:

- compare page versions before re-ingesting;
- deprecate old chunks instead of deleting them;
- skip archive/meeting/report/credential pages;
- do not ingest tokens, passwords, private endpoints, or personal secrets;
- propose summary/index changes instead of auto-changing project policy.

## Security and privacy

Do not commit:

- `~/.codex/config.toml`;
- `.env` files;
- API keys, PATs, Bearer tokens, Basic auth strings;
- generated output containing customer/company data;
- raw Confluence/Jira knowledge dumps unless your team explicitly wants that private repo to hold them;
- screenshots or documents containing credentials.

`.gitignore` blocks common local secret and generated-output paths. Still, always run a secret scan before pushing.

Suggested checks:

```bash
rg -n "token|api[_-]?key|secret|password|Authorization|Bearer|Basic " .
git diff --cached --name-only
git diff --cached
```

## Development

Run tests:

```bash
python3 -m unittest discover -s tests -v
```

Useful CLI help:

```bash
python3 skills/product-core/scripts/product_memory.py --help
python3 skills/product-core/scripts/product_memory.py recall --help
python3 skills/product-core/scripts/product_memory.py validate-artifact --help
```

## Typical prompts

Analyze a requirement:

```text
Use product-core then analyze-requirement. Review this requirement and tell me if it is grooming-ready.
```

Write a ticket:

```text
Use write-ticket. Draft a Jira ticket for this behavior, save it to outputs/ticket-description.
```

Write a PRD:

```text
Use write-prd. Draft a PRD from this Confluence page and Figma screen.
```

Draw a sequence:

```text
Use draw-sequence. Create a Mermaid sequence diagram for this API flow.
```

Stress-test a plan:

```text
Use grilling. Grill this PRD one assumption at a time.
```

Sync knowledge:

```text
Use sync-knowledge. Check the configured Confluence pages and re-ingest changed versions.
```

## Design principles

- Source-backed over chat-memory-backed.
- Ask only blocking clarification questions.
- Vietnamese user-facing output by default; preserve English technical terms.
- Do not invent missing business behavior.
- Small modular skills over one giant prompt.
- Governed changes go to proposals.
- Deprecated knowledge is retained for auditability.
- Generated artifacts should be validated before handoff.

