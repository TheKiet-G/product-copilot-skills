---
name: query-marketing-solution
description: Generate, review, and explain source-backed read-only SQL for Marketing Solution data, beginning with Task List tracking in promotion_coordinator. Use when the user asks to query campaign, task, reward, milestone, user action, status, request time, or extraInfos data; translate a natural-language investigation into SQL; or debug an existing Marketing Solution query.
---

# Query Marketing Solution

Generate SQL from durable project knowledge without inventing tables, fields, or business semantics.

## Workflow

1. Recall context before writing SQL:

```bash
python3 skills/product-core/scripts/product_memory.py recall \
  --project growth-enablement \
  --query "<question + entity + fields>" \
  --budget 5000 \
  --max-results 12
```

2. Identify the dataset and grain. For Task List back-end tracking, read
   [references/task-list-tracking.md](references/task-list-tracking.md).
3. Ask only a blocking question when a missing value changes query meaning, such as date range,
   campaign, user scope, success/failure semantics, or action type. Do not ask for values already
   present in the request.
4. Generate `SELECT` or CTE-based read-only SQL only. Never generate mutation or DDL statements
   unless the user explicitly changes the scope and supplies the relevant data contract.
5. Apply a partition predicate (`ymd` preferred for a bounded day range, otherwise `ym`) and a
   conservative `LIMIT` for exploratory queries. Explain when the source does not define a field
   or dialect behavior.
6. Return:
   - runnable SQL;
   - a short explanation of filters and result grain;
   - assumptions or unresolved schema gaps;
   - optional follow-up SQL only when it materially helps the investigation.

## Query rules

- Use the observed physical SQL column names from the selected schema reference. Use aliases only
  to improve output readability.
- Treat `campaigncode` as `scenarioCode` for Task List only because the source explicitly defines
  that mapping.
- Treat `status = 1` as success; do not assume meanings for other status values.
- Use `json_extract`/`json_extract_scalar` only when compatible with the user's query engine. If
  the engine is unknown and JSON predicates matter, state the assumed dialect.
- Never place real credentials, access tokens, or unnecessary personal data in generated SQL.
- Keep provided `userID` values scoped to the response; do not persist them into skill references
  or durable knowledge.
- Do not claim that generated SQL was executed. Execute only when a read-only data connector is
  available and the user asks for results.

## Output pattern

```sql
SELECT
  *
FROM promotion_coordinator
WHERE 1 = 1
  AND ymd = '<YYYYMMDD>'
  AND campaigntype = 'task_list'
  AND campaigncode = '<SCENARIO_CODE>'
  AND status = 1
ORDER BY requesttime DESC
LIMIT 200;
```

Adapt the projection and filters to the question. Avoid `SELECT *` when the requested output has a
clear, narrow set of fields.
