---
name: grilling
description: Relentlessly stress-test a ticket, PRD, proposal, or decision one assumption at a time. Use before finalizing any artifact when you want to expose unvalidated assumptions, silent business rules, or missing edge cases before committing.
---

# Grilling

Stress-test relentlessly. One question per round. Never proceed to the next question before the current assumption is resolved.

## Format — every question uses this structure

```
**Q [N]:** [Assumption or decision being tested — stated as a question]

**My take:** [Recommended answer or expected behavior — give a concrete position, not "it depends"]

**Why I ask:** [What breaks or changes if the assumption is wrong]
```

## Workflow

1. Recall relevant context via `product-core` for the target project.
2. Identify the artifact or decision to stress-test (ticket, PRD section, proposal, verbal plan).
3. Map the assumption tree: what must be true for this to work correctly?
4. Start with the highest-stakes assumption. Work depth-first — follow a branch until it's resolved before moving to the next.
5. After each answer:
   - If the answer confirms the assumption: acknowledge, move to the next open branch.
   - If the answer conflicts with a prior answer or a known fact in the knowledge base: surface the conflict explicitly before continuing.
   - If the answer reveals a new unknown: push deeper before moving on.
6. Stop when: all major branches are validated, the user calls stop, or the artifact is reclassified as blocked.

## GE-specific assumption categories

Check the following when relevant — do not run all checks on every artifact:

**Budget and stock**
- Scope: per-campaign, per-user, per-mktCode, or global?
- Exhaustion behavior: hide, disable, reject, or retry?
- Concurrent redemption: race condition handled how?
- Top-up / reset: allowed? who triggers? what happens to in-flight requests?

**Promotion mechanics**
- Rule precedence when multiple promotions apply simultaneously?
- Idempotency: same user, same trigger, second call — what happens?
- Multi-promotion stacking: allowed, capped, or blocked?
- Voucher state machine: which transitions are valid, which are irreversible?

**Campaign lifecycle**
- Who can transition from each state? What guard conditions apply?
- What happens to in-progress user claims when a campaign is paused or expired?
- Rollback: is it possible? what is the blast radius?

**User and permission**
- Which user states are eligible? (active, KYC level, wallet state, segment)
- What does a user see vs. what does the system silently reject?

**API and integration**
- Backward compatible? Does the caller need to change?
- Timeout behavior and retry safety — idempotent or not?
- Async vs. sync: who holds the user waiting?

**NBA workflow**
- Trigger: event-based or scheduled? What fires it?
- Delay rules: what clock is used? What if the user's state changes during delay?
- What downstream actions are taken, and are they reversible?

**Data and observability**
- Source of truth when GP and ZPPROM disagree?
- What is logged for audit? Who can query it?
- Is there a metric or alert that would catch a regression in production?

## Stopping conditions

- All major assumption branches resolved → summarize confirmed assumptions and flag any remaining open questions.
- User says stop → summarize what was confirmed, what remains open, and what the artifact's readiness status is.
- 3+ consecutive answers reveal new unknowns with no resolution → classify the artifact as **blocked**, list blockers explicitly.

## After grilling

If the artifact should be drafted or revised, hand off to the appropriate skill:
- Ticket → `write-ticket`
- PRD → `write-prd`
- Diagram → `draw-sequence`

Document confirmed assumptions as source-backed facts via `product-core learn` if they are durable and non-sensitive. Send business rules and policy-level findings to `product-core propose`.
