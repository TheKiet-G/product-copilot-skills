# Task List tracking schema

Source of truth: `confluence://GP/pages/219686355?version=27`  
Page: `Task List tracking`  
URL: `https://confluence.zalopay.vn/display/GP/Task+List+tracking`

Use this reference only for Task List. Recall the live project knowledge when freshness matters.

## Dataset

- Logical table used by existing investigations: `promotion_coordinator`
- HDFS path:
  `hdfs://zalopaynewcluster/zalopay/encrypt/growthenablement/grownenablement_promotioncampaign/promotion_coordinator`
- Task List discriminator: `campaignType = 'task_list'`
- Partition fields observed in the user-provided query: `ym`, `ymd`

## Coordinator fields

Confluence labels fields in camelCase, while the working SQL supplied by the user shows lowercase
physical column names. Generate SQL using the lowercase names below.

| Physical SQL column | Confluence label | Type | Source meaning |
|---|---|---|---|
| `campaigntype` | `campaignType` | String | `task_list` for Task List |
| `campaigncode` | `campaignCode` | String | Equals Task List `scenarioCode` |
| `campaignname` | `campaignName` | String | Campaign name; currently set to `scenarioCode` |
| `requesttime` | `requestTime` | Long (millisecond) | Time of action |
| `actiontype` | `actionType` | String | `ACCEPT_TASK`: user accepts a task; `ISSUE_TASK`: user completes a task |
| `stamptype` | `stampType` | String | `TASK` |
| `reftrans` | `refTrans` | Long | TPE `ZPTransID`; equals `sourceTransID` in present API |
| `userid` | `userID` | Long | ZaloPay user ID |
| `zaloid` | `zaloID` | String | User Zalo ID |
| `status` | `status` | Long | `1`: success; all other values: failure |
| `extrainfos` | `extraInfos` | Object | Action-specific fields below |

The `extraInfos` specification also defines `CLAIM_REWARD` and milestone-completion payloads.
Because the Coordinator summary does not enumerate every action type, do not assume the list above
is exhaustive.

## extraInfos core fields

Available across `ACCEPT_TASK`, `ISSUE_TASK`, and `CLAIM_REWARD` payload definitions:

| Field | Type | Meaning |
|---|---|---|
| `taskName` | String | Name configured in Task Module |
| `taskDetail` | String/ID | Task ID from Task Module |
| `universalTask` | Boolean | Universal-task flag |
| `interactiveMode` | Boolean | Interactive-mode flag |
| `progressType` | String | Progress tracking type |
| `currentProgress` | Long | Current progress |
| `targetProgress` | Long | Target progress |
| `autoReward` | Boolean | `true`: no manual claim required; `false`: user must claim |

## Milestone fields

Send milestone fields only when the task belongs to a sequence / Sequence Milestones Task List:

| Field | Type | Meaning / values |
|---|---|---|
| `milestoneGroup` | String | Milestone group, example `NPU` |
| `milestoneOrder` | Long | Order in milestone group |
| `milestoneStatus` | String | `processing` or `finished` |
| `total_Milestones_in_group` | Long | Total milestones in the group |

The source also shows a milestone completion payload containing `milestoneGroup`,
`milestoneOrder`, and `total_Milestones_in_group`. Confirm the exact `actionType` before filtering
production data because the rendered Confluence table does not preserve that row boundary clearly.

## Reward fields

Present for reward-bearing task or milestone payloads:

| Field | Type | Meaning |
|---|---|---|
| `rewardPool` | Long | Reward Module pool ID |
| `rewardName` | String | Reward name |
| `rewardQuantity` | Long | Quantity received |
| `rewardAmount` | Long | Face value, for example VND or coin amount |
| `presentID` | Long | Present issuance ID |

## Query conventions

- Bound scans using `ymd IN ('YYYYMMDD', ...)` or `ym IN ('YYYYMM', ...)`.
- Use `requesttime` for event ordering or millisecond time windows.
- Use `status = 1` when the question asks for successful events.
- Add `stamptype = 'TASK'` when isolating Task List task records.
- Query `extraInfos` with the JSON functions supported by the actual engine. The existing example
  uses `json_extract(extrainfos, '$.rewards')` and JSON literal `JSON '[]'`, which resembles a
  Trino/Presto-style expression but does not by itself prove the engine.
- Do not embed a real `userID` or campaign code in reusable examples; use placeholders.
