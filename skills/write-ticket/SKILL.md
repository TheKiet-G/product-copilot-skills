---
name: write-ticket
description: Draft source-backed product ticket descriptions in Vietnamese while preserving English technical terms. Use when creating, revising, or validating a Jira-style ticket, user story, acceptance criteria, implementation-ready requirement, or ticket derived from project documents.
---

# Write Ticket

1. Recall context with `product-core`; do not load the entire knowledge base.
2. Apply `product-core/references/clarification-policy.md`. Ask blocking clarification questions in Vietnamese and wait for answers.
3. Run `python3 skills/product-core/scripts/product_memory.py template-status --type ticket`.
4. Read [references/change-request-rules.md](references/change-request-rules.md). Use its Long Version questions only for relevant missing information.
5. If the template is not installed, produce a clearly labeled **DRAFT — TEMPLATE REQUIRED**, list missing inputs, and do not claim the ticket is final.
6. Analyze ambiguity, business rules, dependencies, edge cases, and acceptance criteria.
7. Render `Context`, `Requirement`, and `Acceptance Criteria` in that order.
8. Under `Requirement`, choose exactly one: `Product`, `Back-end & Front-end Technical`, or `Configuration`.
9. Add artifact metadata and source references.
10. Validate with `validate-artifact --type ticket --file <path>`.
11. Propose durable new learning through `product-core`; do not silently alter policy or template.

## Output file (bắt buộc)

Sau khi draft xong, **luôn lưu ra file** tại `outputs/ticket-description/` theo naming convention sau:

```
outputs/ticket-description/<TICKET-ID>_<YYYY-MM-DD>_<slug>.md
```

- `<TICKET-ID>`: ID Jira nếu có (ví dụ `GE-23680`), nếu không có dùng `DRAFT`
- `<YYYY-MM-DD>`: ngày generate (lấy từ `generated_at`)
- `<slug>`: 3–5 từ mô tả nội dung ticket, lowercase, dấu gạch ngang

**Ví dụ:** `outputs/ticket-description/GE-23680_2026-06-29_count-voucher-out-of-budget.md`

Sử dụng format từ [templates/ticket/jira-output-template.md](../../templates/ticket/jira-output-template.md):
- Metadata đặt trong HTML comment `<!-- ... -->` ở đầu file — không hiển thị khi paste
- Section heading dùng `h3.` (Jira/Confluence wiki markup)
- Sub-label (Product / Technical / Configuration) dùng `*bold*` (single asterisk)
- Separator giữa các section dùng `----`
- Bullet list dùng `*` prefix
- Tương thích copy trực tiếp lên Jira classic editor và Confluence

Sau khi lưu file, thông báo đường dẫn file cho user.

Default to Vietnamese prose and retain API names, field names, domain terms, and code identifiers in English.

Read [references/ticket-quality.md](references/ticket-quality.md) for the quality gate.
