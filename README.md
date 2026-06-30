# Product Copilot Skills

Bộ skill Product Copilot dạng portable, Git-backed, dùng được cho Codex, Claude Code, Cursor và các agent client khác.

Repo này biến một coding/product assistant thông thường thành Product Copilot có khả năng làm việc dựa trên nguồn dữ liệu bền vững. Nó giúp team Product đọc lại knowledge cũ, hỏi đúng câu clarification, viết Jira ticket, viết PRD, vẽ sequence diagram, trace requirement giữa nhiều artifact, và cập nhật knowledge base một cách an toàn thay vì phụ thuộc vào chat history.

Ý tưởng lõi:

1. Lưu product context có thể tái sử dụng trong `knowledge/`.
2. Route mỗi product task qua các skill nhỏ, rõ trách nhiệm trong `skills/`.
3. Không tự ý sửa business rules, templates, policies; mọi thay đổi governed đi qua proposal.
4. Validate artifact trước khi handoff.

## Repo này giải quyết bài toán gì?

Product work thường bị gãy vì context nằm rải rác trong chat, Confluence, Jira, Figma, screenshot hoặc trí nhớ của một vài người. Một AI chat thông thường có thể trả lời tốt trong một session, nhưng qua session khác lại quên context cũ hoặc âm thầm tự bịa business behavior còn thiếu.

Bộ skill này được thiết kế để xử lý các vấn đề đó:

- Recall context cũ có source rõ ràng qua nhiều session.
- Biến Confluence/Jira/project knowledge thành Markdown/JSONL có thể search bằng Git-backed memory.
- Tách rõ facts, assumptions, open questions và proposed business rules.
- Sinh artifact tiếng Việt nhưng giữ nguyên English technical terms.
- Chuẩn hóa workflow viết ticket, PRD, sequence diagram, traceability và requirement review.
- Tránh đưa token, API key, local config hoặc generated output riêng tư lên source control.

## Cấu trúc repo

```text
.
├── AGENTS.md                         # Adapter cho Codex
├── CLAUDE.md                         # Adapter cho Claude Code
├── .cursor/rules/product-copilot.mdc # Adapter cho Cursor
├── config/product-copilot.json       # Config safe learning / governed learning
├── skills/                           # Các Product Copilot skills dạng module
├── templates/                        # Ticket / PRD templates và template status
├── knowledge/                        # Khung Git-backed memory
│   ├── global/                       # Skeleton cho global context nếu cần
│   └── projects/_template/           # Template rỗng cho project mới
└── tests/                            # Regression tests cho CLI
```

Các file generated, private Confluence/Jira ingests, proposals, audit logs và local secrets được ignore trong `.gitignore`.

## Danh sách skill

| Skill | Dùng để làm gì | Khi nào dùng |
|---|---|---|
| `product-core` | Memory layer: init project knowledge, ingest document, recall context, learn safe facts, propose governed changes, validate artifacts. | Luôn chạy đầu tiên với product task cần context/source. |
| `analyze-requirement` | Phân tích requirement về ambiguity, business rules, edge cases, dependencies, acceptance criteria và readiness. | Trước khi viết ticket/PRD hoặc khi requirement còn mơ hồ. |
| `write-ticket` | Draft Jira-style ticket bằng tiếng Việt, có metadata source và acceptance criteria. | Khi cần tạo/sửa Jira ticket đủ rõ để grooming/dev. |
| `write-prd` | Draft PRD có source, stable requirement IDs, assumptions và open questions. | Khi cần viết PRD từ Confluence, Figma, ticket, discovery notes hoặc project knowledge. |
| `draw-sequence` | Tạo Mermaid sequence diagram cho API/service/user/event flow. | Khi cần visualize happy path, error path, retry, timeout, async interaction. |
| `trace-artifacts` | Kiểm tra consistency và traceability giữa ticket, PRD, acceptance criteria và sequence diagram. | Trước grooming/handoff hoặc khi nhiều artifact có nguy cơ lệch nhau. |
| `sync-knowledge` | So sánh version page Confluence đã ingest với live Confluence, rồi re-ingest page thay đổi. | Sau khi Confluence update hoặc nghi ngờ knowledge stale. Cần Atlassian MCP/connector. |
| `query-marketing-solution` | Chuyển câu hỏi tự nhiên thành SQL read-only dựa trên schema Marketing Solution đã có source; hiện hỗ trợ Task List tracking trên `promotion_coordinator`. | Khi cần query/debug campaign, task, reward, milestone, action, status hoặc `extraInfos`. |
| `grilling` | Stress-test assumption từng câu một trước khi finalize artifact/decision. | Khi muốn review gắt PRD/ticket/plan trước khi commit hướng làm. |

## Các skill phối hợp với nhau như thế nào?

Workflow chuẩn cho product task:

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
safe learning hoặc governed proposal
```

Ví dụ:

- Viết Jira ticket: `product-core` → `write-ticket`
- Viết PRD: `product-core` → `write-prd`
- Review requirement: `product-core` → `analyze-requirement`
- Vẽ sequence diagram: `product-core` → `draw-sequence`
- Cross-check PRD/ticket/diagram: `product-core` → `trace-artifacts`
- Sync Confluence knowledge: `product-core` → `sync-knowledge`
- Query dữ liệu Marketing Solution: `product-core` → `query-marketing-solution`

`product-core` được tách riêng khỏi các drafting skills. Nó phụ trách memory và governance; các task skill chỉ tập trung vào một loại artifact.

## Agent adapters

Mỗi AI client đọc instruction file khác nhau, nhưng tất cả đều trỏ về cùng một skill source:

- Codex đọc `AGENTS.md`.
- Claude Code đọc `CLAUDE.md`.
- Cursor đọc `.cursor/rules/product-copilot.mdc`.
- Claude slash-style commands nằm trong `.claude/commands/`.

Adapter chỉ nên mỏng và trung lập. Source of truth luôn là `skills/*/SKILL.md`.

## Quick start

Cài dependencies:

```bash
python3 -m pip install -r requirements.txt
```

Khởi tạo memory space cho project:

```bash
python3 skills/product-core/scripts/product_memory.py init-project \
  --project my-project
```

Ingest local document:

```bash
python3 skills/product-core/scripts/product_memory.py ingest \
  --project my-project \
  --source path/to/document.md
```

Ingest text export từ Confluence:

```bash
confluence-export-command | python3 skills/product-core/scripts/product_memory.py ingest-text \
  --project my-project \
  --source "confluence://SPACE/pages/PAGE_ID?version=N" \
  --title "Page title"
```

Recall context liên quan:

```bash
python3 skills/product-core/scripts/product_memory.py recall \
  --project my-project \
  --query "budget alert validation for promotion campaigns" \
  --budget 12000 \
  --max-results 20
```

Validate artifact:

```bash
python3 skills/product-core/scripts/product_memory.py validate-artifact \
  --type ticket \
  --file outputs/ticket-description/GE-123_example.md
```

## Memory và governance model

`product-core` có 2 đường cập nhật knowledge.

### Safe learning

Dùng `learn` cho facts có source rõ và ít rủi ro:

- glossary terms;
- source links;
- explicit system facts;
- non-sensitive preferences;
- approved decisions.

Ví dụ:

```bash
python3 skills/product-core/scripts/product_memory.py learn \
  --project growth-enablement \
  --kind glossary \
  --statement "Promotion Code is a CRM campaign where a user enters a code to receive a configured reward if rules pass." \
  --source "confluence://GP/pages/333516693?version=75"
```

### Governed proposals

Dùng `propose` cho các nội dung không nên tự động trở thành sự thật:

- business rules;
- policies;
- templates;
- agent instructions;
- conflict resolution;
- inferred behavior có confidence thấp.

Ví dụ:

```bash
python3 skills/product-core/scripts/product_memory.py propose \
  --project growth-enablement \
  --kind business-rule \
  --statement "Budget Alert threshold must be an integer from 1 to 99." \
  --source "confluence://GP/pages/329219233?version=74"
```

Command này tạo pending JSON proposal dưới `knowledge/proposals/` trong working tree. Với source repo này, project-specific proposals được ignore mặc định vì thường chứa internal project context.

## Artifact templates

Templates nằm trong `templates/`.

Ticket template status:

```text
templates/ticket/template.json
```

PRD template status:

```text
templates/prd/template.json
```

Install approved template:

```bash
python3 skills/product-core/scripts/product_memory.py install-template \
  --type ticket \
  --file templates/ticket/change-request-template.md \
  --version 2026-06-16 \
  --heading "Context" \
  --heading "Requirement" \
  --heading "Acceptance Criteria"
```

Nếu template chưa được install, validation của artifact tương ứng sẽ fail có chủ đích. Đây là guardrail để assistant không được trình bày artifact như final khi approved template còn thiếu.

## Cách dùng với Confluence và Jira

Repo này không lưu credentials.

Dùng local MCP connector, browser session hoặc export command để lấy nội dung Confluence/Jira, sau đó ingest phần page body đã được sanitize qua `product_memory.py`.

Định dạng source khuyến nghị:

```text
confluence://SPACE/pages/PAGE_ID?version=N
jira://PROJECT/ISSUE-ID
figma://FILE_ID/node/NODE_ID
```

Khi sync Confluence bằng `sync-knowledge`, giữ các nguyên tắc:

- so sánh page version trước khi re-ingest;
- deprecate old chunks thay vì xóa;
- skip archive/meeting/report/credential pages;
- không ingest token, password, private endpoint hoặc personal secrets;
- propose thay đổi summary/index thay vì auto-change project policy.

## Security và privacy

Không commit:

- `~/.codex/config.toml`;
- `.env` files;
- API keys, PATs, Bearer tokens, Basic auth strings;
- generated output có customer/company data;
- raw Confluence/Jira knowledge dumps, trừ khi team chủ động muốn private repo này giữ dữ liệu đó;
- screenshots hoặc documents có credentials.

`.gitignore` đã chặn các path local secret và generated output phổ biến. Tuy vậy, trước khi push vẫn nên scan lại.

Suggested checks:

```bash
rg -n "token|api[_-]?key|secret|password|Authorization|Bearer|Basic " .
git diff --cached --name-only
git diff --cached
```

## Development

Chạy tests:

```bash
python3 -m unittest discover -s tests -v
```

CLI help:

```bash
python3 skills/product-core/scripts/product_memory.py --help
python3 skills/product-core/scripts/product_memory.py recall --help
python3 skills/product-core/scripts/product_memory.py validate-artifact --help
```

## Prompt mẫu

Analyze requirement:

```text
Use product-core then analyze-requirement. Review this requirement and tell me if it is grooming-ready.
```

Write ticket:

```text
Use write-ticket. Draft a Jira ticket for this behavior, save it to outputs/ticket-description.
```

Write PRD:

```text
Use write-prd. Draft a PRD from this Confluence page and Figma screen.
```

Draw sequence:

```text
Use draw-sequence. Create a Mermaid sequence diagram for this API flow.
```

Stress-test plan:

```text
Use grilling. Grill this PRD one assumption at a time.
```

Sync knowledge:

```text
Use sync-knowledge. Check the configured Confluence pages and re-ingest changed versions.
```

## Nguyên tắc thiết kế

- Source-backed hơn chat-memory-backed.
- Chỉ hỏi blocking clarification questions.
- User-facing output mặc định bằng tiếng Việt; giữ nguyên English technical terms.
- Không tự bịa missing business behavior.
- Dùng nhiều modular skills nhỏ thay vì một prompt khổng lồ.
- Governed changes đi qua proposals.
- Deprecated knowledge được giữ lại để audit.
- Generated artifacts cần được validate trước khi handoff.
