# Change Request Rules

Source: `Change+Request+Template.doc`, Confluence export dated 2026-06-16.

## Output Structure

Always produce these sections in order:

1. `Context`
2. `Requirement`
3. `Acceptance Criteria`

Under `Requirement`, include exactly one variant:

- `Product`: user-facing UI, flow, or behavior
- `Back-end & Front-end Technical`: API, database, service, architecture, or other technical change not directly visible to users
- `Configuration`: configuration-only change without code-logic changes

For mixed UI and back-end changes, choose the variant representing most of the scope. Describe the remainder within it or recommend child tickets when the combined scope is not independently groomable.

Skip irrelevant details instead of writing `N/A`. Be concrete: name fields, endpoints, services, states, and expected outcomes when known.

## Clarification Questions

Use only relevant questions. Ask in Vietnamese and wait when the answer materially affects the ticket.

### Context

- Vì sao cần thay đổi?
- Business goal, user pain point hoặc current problem cụ thể là gì?

### Product

- Những user hoặc permission state nào bị ảnh hưởng?
- Entry point nằm ở screen, CTA, tab, icon hay deeplink nào?
- UI component hoặc layout nào thay đổi?
- Cần xử lý state nào: default, loading, empty, success, error, disabled hay expired?
- User thực hiện action nào và system response sau từng action là gì?
- Có edge case về null/zero, no data, long text, multiple records hoặc out-of-range value không?
- Cần event tracking nào?
- Có Figma, mockup, prototype, demo hoặc reference screen không?

Không bắt buộc có Figma, nhưng Product change phải có mô tả đủ chi tiết hoặc sketch để FE/QA không hiểu sai.

### Back-end & Front-end Technical

- Thay đổi kỹ thuật cụ thể là gì?
- Có thay đổi database hoặc data migration không?
- Request/response structure dự kiến là gì?
- Service nào tham gia và dependency giữa chúng là gì?
- Có thay đổi service configuration hoặc technology stack không?
- Có cần diagram để hiểu scope không?
- Có Figma, mockup, prototype, demo hoặc reference screen không?

### Configuration

- Configuration nào thay đổi và nằm ở Tool/File/Database/Redis/CMDB nào?
- Cách áp dụng thay đổi là gì?
- Có cần restart service không; nếu có, service nào?

### Acceptance Criteria

- Điều kiện observable nào xác nhận ticket hoàn thành?
- Cần deploy đến environment nào?
- Có yêu cầu tracking, logging, monitoring hoặc alerting không?
- Có rollout plan, feature flag, migration hoặc backfill không?
