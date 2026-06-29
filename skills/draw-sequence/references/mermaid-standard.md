# Mermaid Sequence Standard

Use a fenced `mermaid` block containing `sequenceDiagram` and `autonumber`. Declare every participant. Prefer short aliases and full display labels.

Use solid arrows for calls and dashed arrows for responses. Use notes for requirement IDs, not long prose. Represent conditional and failure behavior with Mermaid control blocks. Avoid styling directives and experimental syntax to maximize renderer compatibility.

Pass when syntax is valid, participants are declared, the happy path is complete, known failures appear, and every interaction traces to a source or an explicit assumption.
