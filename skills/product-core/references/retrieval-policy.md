# Retrieval Policy

Rank active facts and document chunks using lexical term overlap, phrase matches, recency, project scope, and source confidence. Project facts outrank global facts when scores tie.

Use these default character budgets:

- Requirement analysis: 12,000
- Ticket: 10,000
- PRD: 18,000
- Sequence diagram: 8,000
- Traceability review: 14,000

Return summaries and facts before chunks. Read full source files only when retrieved evidence is insufficient. Exclude deprecated entries unless the query asks for history.
