<!--
template_status: DRAFT — TEMPLATE PROPOSAL
template_name: Growth Enablement PRD
based_on: confluence://GP/pages/333516693?version=75
project: growth-enablement
language: vi

Hướng dẫn:
- Giữ toàn bộ section BẮT BUỘC.
- Chỉ thêm section ĐIỀU KIỆN khi feature thực sự có behavior tương ứng.
- Xóa hướng dẫn trong dấu [ ] trước khi publish.
- Không biến assumption hoặc open question thành business rule.
-->

# [Tên feature / initiative]

## 0. General Information

| Field | Value |
|---|---|
| Document status | Draft / In Review / Approved / Deprecated |
| Owner | [Product Owner] |
| Business stakeholder | [Tên/nhóm] |
| Technical stakeholder | [Tên/nhóm] |
| Created date | [YYYY-MM-DD] |
| Latest update | [YYYY-MM-DD] |
| Target release | [Nếu đã xác nhận] |
| Jira / Figma / Related docs | [Link] |

### Version Control

| Date | Version | Change | Updated by |
|---|---:|---|---|
| [YYYY-MM-DD] | 0.1 | Initial draft | [Tên] |

---

## 1. Background & Problem Statement

### Background

[Mô tả bối cảnh hiện tại, system/process liên quan và lý do cần thay đổi.]

### Problem

[Nêu vấn đề quan sát được. Tách symptom, root cause đã được xác nhận và phần
chưa đủ evidence.]

### Evidence

- [Signal/data/ticket/user feedback — kèm source]
- [Current behavior — kèm source]

### Affected Users

- [User/actor]
- [Pain point hoặc unmet need]

---

## 2. Objective & Success Measures

### Objective

[Kết quả mong muốn, không mô tả solution chi tiết.]

### Success Metrics

| Metric | Baseline | Target | Measurement window | Source |
|---|---:|---:|---|---|
| [Metric] | [Nếu có] | [Không tự đặt nếu chưa xác nhận] | [Khoảng thời gian] | [Nguồn] |

### Guardrails

- [Metric hoặc điều kiện không được xấu đi]

---

## 3. Scope

### In Scope

- [Behavior/capability thuộc lần triển khai này]

### Out of Scope

- [Nội dung chủ động loại khỏi phạm vi]

### Assumptions

- [ASSUMPTION — cần kiểm chứng]

### Dependencies

- [System/team/data/policy/vendor]

---

## 4. User Journeys & Use Cases

### Actors

| Actor | Goal | Permission / constraint |
|---|---|---|
| [Actor] | [Goal] | [Nếu có] |

### Primary Flow

1. [Actor thực hiện hành động]
2. [System phản hồi]
3. [Kết quả quan sát được]

### Alternative / Failure Flows

- [Validation failure]
- [Permission failure]
- [Timeout/partial failure/retry/recovery nếu liên quan]

---

## 5. Requirements

> Mỗi requirement phải có ID ổn định, source và acceptance criteria kiểm thử
> được. Không gộp nhiều behavior độc lập vào một requirement. Requirement mô
> tả intent và behavior cấp cao; đặc tả component chi tiết nằm ở Section 6.

### REQ-001 — [Tên requirement]

- **Intent:** [Giá trị hoặc behavior cần đạt]
- **Actor:** [Ai/hệ thống nào]
- **Preconditions:** [Điều kiện đầu vào]
- **Behavior:** [System phải làm gì]
- **Validation:** [Rule kiểm tra input/state/permission]
- **Error handling:** [Phản hồi khi thất bại]
- **Source:** [Confluence/Jira/Figma/decision]

**Acceptance Criteria**

- **Given** [bối cảnh]
  **When** [hành động]
  **Then** [kết quả quan sát được]

### REQ-002 — [Tên requirement]

[Lặp lại cấu trúc REQ-001.]

---

## 6. Detailed Specification

> Đây là phần đặc tả chính để Product, Design, FE, BE và QC cùng grooming.
> Chia nội dung theo Screen → Section → Component. Mỗi component phải có một
> dòng riêng; không gom nhiều field có validation khác nhau vào cùng một dòng.

### 6.1. [Screen / Page / Flow Name]

- **Requirement mapping:** [REQ-001, REQ-002]
- **Figma / wireframe:** [Link hoặc ảnh]
- **Entry point:** [User đi vào màn hình từ đâu]
- **Actors / permission:** [Ai được view/create/edit/approve]
- **Purpose:** [Màn hình giải quyết việc gì]

#### 6.1.1. [Section Name]

| Field / Component | UI Type | Description & Behavior | Data / Mapping | Default | Validation & Error Message | Permission / Edit Rule |
|---|---|---|---|---|---|---|
| [Component name] | Textbox / Dropdown / Date Picker / Table / CTA / Badge / Section / API | [Component hiển thị gì; user tương tác thế nào; system phản hồi ra sao] | [Source field/API/entity] | [Giá trị mặc định] | [Required, format, min/max, dependency và exact error behavior] | [Role/state nào được view/edit; hide hay disable] |

**Section behavior**

- **Load:** [Loading, pagination, sorting, data refresh]
- **Empty state:** [Nội dung và CTA]
- **Error state:** [Inline/toast/modal; retry behavior]
- **Save/Submit:** [Trigger, validation order, confirmation và kết quả]
- **Cancel/Back:** [Unsaved-change behavior]

#### 6.1.2. [Section Name]

[Lặp lại bảng component và Section behavior.]

### 6.2. [Screen / Page / Flow Name]

[Lặp lại cấu trúc 6.1.]

### Component Specification Rules

- Textbox phải nêu: data type, min/max length, accepted characters, trim/case
  normalization, placeholder và error message.
- Dropdown phải nêu: single/multi-select, option source, sorting, dependency,
  default và behavior khi option inactive.
- Date/Time phải nêu: timezone, inclusive/exclusive boundary, range limit và
  behavior khi active time đã bắt đầu/kết thúc.
- Table/List phải nêu: columns, mapping, sorting, filter, pagination, empty
  state và row actions.
- CTA phải nêu: enable/disable condition, permission, confirmation, API action,
  loading, success và failure behavior.
- Status/Badge phải nêu: source state, display label, color meaning và allowed
  transition nếu có.
- Upload phải nêu: file type, size, dimension, quantity, validation và
  replace/remove behavior.
- API-only component phải nêu: request trigger, required input, response
  mapping, error mapping, timeout/retry/idempotency nếu liên quan.

---

## 7. UX & Content

- **Figma / prototype:** [Link]
- **Entry point / navigation:** [Nếu có]
- **Loading / empty / error / success states:** [Mô tả]
- **Permission visibility:** [Ẩn, disable hay báo lỗi]
- **Localization / accessibility:** [Nếu liên quan]
- **Tracking events:** [Event name, trigger, properties — nếu đã xác nhận]

---

## 8. Business Rules & Validation

| Rule ID | Rule | Priority / precedence | Source | Status |
|---|---|---|---|---|
| BR-001 | [Business rule đã được xác nhận] | [Nếu conflict] | [Nguồn] | Confirmed / Pending |

> Rule chưa được approve phải để `Pending` và đưa vào Open Questions; không
> dùng như current behavior.

---

## 9. Data, Integration & Non-functional Requirements

### Data

- [Entity/field/source of truth/retention/migration nếu liên quan]

### Integration

- [API/event/upstream/downstream]
- [Backward compatibility/idempotency/timeout/retry nếu liên quan]

### Non-functional

- **Performance:** [SLO/limit nếu đã xác nhận]
- **Security & privacy:** [Permission, audit, sensitive data]
- **Observability:** [Logs, metrics, alert]
- **Availability / recovery:** [Nếu liên quan]

---

## 10. Rollout & Operations

- **Rollout strategy:** [Feature flag/phased rollout/full release]
- **Migration/backfill:** [Nếu có]
- **Monitoring:** [Dashboard/metric/alert]
- **Rollback:** [Trigger và cách rollback]
- **Operational owner:** [Team/PIC]

---

## 11. Risks, Open Questions & Decisions

### Risks

| Risk | Impact | Mitigation | Owner |
|---|---|---|---|
| [Risk] | [Impact] | [Mitigation] | [Owner] |

### Open Questions

- [BLOCKING/NON-BLOCKING] [Câu hỏi] — Owner: [Tên]

### Decision Log

| Date | Decision | Rationale | Approver |
|---|---|---|---|
| [YYYY-MM-DD] | [Decision] | [Lý do] | [Tên] |

---

## 12. Traceability

| Requirement | Jira | Figma | API/Event | Acceptance Test | Status |
|---|---|---|---|---|---|
| REQ-001 | [Link] | [Link] | [Reference] | [Test ID] | Draft / Ready |

---

# Conditional Modules

> Chỉ chèn module phù hợp vào PRD, tại vị trí gần requirement liên quan nhất.

## [CONDITIONAL] Delivery Phases

Dùng khi scope thực sự được chia thành nhiều release/phase có outcome khác nhau.

| Phase | Outcome | Included requirements | Exit criteria |
|---|---|---|---|
| [Phase] | [Outcome] | [REQ IDs] | [Điều kiện hoàn tất] |

## [CONDITIONAL] Status Lifecycle

Dùng khi entity có state transition ảnh hưởng permission hoặc behavior.

| Current state | Action / trigger | Next state | Actor | Guard condition |
|---|---|---|---|---|
| [State] | [Trigger] | [State] | [Actor/System] | [Condition] |

## [CONDITIONAL] List / Search / Filter

Dùng cho màn hình quản lý danh sách. Khi dùng module này, đặt bảng dưới Screen
tương ứng trong Section 6.

| Field / Control | UI Type | Description & Behavior | Data / Mapping | Default | Validation & Error Message | Permission / Edit Rule |
|---|---|---|---|---|---|---|
| [Field] | [Type] | [Search/filter/display behavior] | [Source] | [Default] | [Rule] | [Rule] |

## [CONDITIONAL] Configuration Form

Dùng cho create/edit/configuration flow. Đây là bảng mở rộng của Detailed
Specification, không thay thế Section 6.

| Field / Component | UI Type | Description & Behavior | Data / Mapping | Required | Default | Validation & Error Message | Permission / Editable States |
|---|---|---|---|---:|---|---|---|
| [Field] | [Type] | [Behavior] | [Source] | Yes/No | [Value] | [Rule] | [Role/states] |

## [CONDITIONAL] Budget / Stock / Limit

Dùng khi feature tạo financial exposure, quota hoặc counter.

- Source of truth: [System]
- Scope: [Campaign/package/user/time period/...]
- Exhaustion behavior: [Hide/disable/reject/retry/...]
- Top-up/reset behavior: [Nếu có]
- Alert/audit requirement: [Nếu có]

## [CONDITIONAL] Approval & Permission Matrix

| Role | View | Create | Edit | Approve | Delete/Archive | Notes |
|---|---:|---:|---:|---:|---:|---|
| [Role] | ✓/– | ✓/– | ✓/– | ✓/– | ✓/– | [Constraint] |

## [CONDITIONAL] Multiple-item Behavior

Dùng khi feature hỗ trợ nhiều reward/item/component trong cùng một entity.

- Cardinality and limits: [Rule]
- Ordering/priority: [Rule]
- Partial failure behavior: [Rule]
- Aggregate budget/stock/validation: [Rule]

## [CONDITIONAL] System Flow / Sequence

Dùng khi có từ ba system interaction trở lên hoặc có retry/rollback/async flow.

- Participants: [Systems/actors]
- Trigger: [Event]
- Happy path: [Reference sequence]
- Failure/retry/rollback: [Behavior]
