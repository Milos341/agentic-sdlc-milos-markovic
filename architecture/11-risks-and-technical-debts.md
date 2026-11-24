# 11. Risks and Technical Debts

This chapter lists known architectural risks and technical debts for the **Wallet Valuation System**. Items are intentionally concise and appropriate for the course-exercise scope. Each item includes a mitigation or follow-up action.

## 11.1 Risks

| ID | Risk | Impact | Likelihood | Mitigation / Follow-up | Related |
|---|---|---|---|---|---|
| **R-1** | **External exchange-rate provider unavailability or instability** | Valuations cannot be completed; users receive valuation-unavailable errors. | Medium | Fail explicitly (ADR-004); map errors at adapter boundary; add timeout/retry/circuit-breaker/caching decisions before production hardening. | ADR-001, ADR-004, QS-2 |
| **R-2** | **Exchange-rate data quality or semantic mismatch** | Incorrect valuation if provider uses unexpected units, stale rates, or incompatible currency/stock mappings. | Medium | Normalize and validate provider responses in the adapter; define supported stock/currency mappings; test with deterministic fakes and adapter contract tests. | ADR-002, QS-1, QS-4 |
| **R-3** | **DynamoDB access-pattern limitations** | Future query needs may be awkward or inefficient; schema changes can be costly. | Medium | Design table keys/access patterns around known wallet load/save and valuation use cases; keep persistence behind `WalletRepository` port. | ADR-001, ADR-002, TC-3 |
| **R-4** | **Lambda cold starts and external-call latency** | First request after idle period or slow provider response may exceed acceptable latency. | Medium | Keep function lightweight; monitor latency; consider timeout configuration and future caching/provider optimization if needed. | ADR-001, R-1 |
| **R-5** | **Missing authentication/authorization** | In a multi-user or public deployment, wallets could be exposed or modified without proper access control. | Low in course scope, High outside scope | Treat as out of scope for the kata; add explicit authn/authz decision before any production or multi-user deployment. | Chapter 3, Chapter 8 |
| **R-6** | **Single Lambda grows too large** | Reduced maintainability and harder independent evolution of wallet management and valuation. | Low initially | Keep internal modular boundaries; review function size/complexity; split into separate functions/services only when justified (ADR-003). | ADR-003, QS-8 |
| **R-7** | **Secret/configuration leakage** | Provider API keys or sensitive runtime config could be exposed in code, logs, or responses. | Low | Use deployment configuration/secret management; never hard-code secrets; avoid logging sensitive data; return generic client errors. | Chapter 7, Chapter 8 |

## 11.2 Technical Debts

| ID | Debt | Why it exists | Impact if not addressed | Planned follow-up | Related |
|---|---|---|---|---|---|
| **TD-1** | **No resilience policy for rate provider** | Initial scope defers timeout/retry/circuit-breaker/caching decisions. | Frequent avoidable failures or poor latency under provider instability. | Define timeout budget; evaluate retries with backoff, circuit breaker, and short-lived rate caching; record as ADR when decided. | ADR-001, ADR-004, R-1 |
| **TD-2** | **DynamoDB schema/access patterns not fully specified** | Architecture defines responsibility but not detailed table key/item schema. | Implementation may require rework or inefficient access patterns. | Specify wallet table schema, keys, and access patterns during implementation; document in code/ADR if significant. | ADR-001, R-3 |
| **TD-3** | **API contract details are incomplete** | Chapter focuses on architecture; request/response schemas, error codes, and idempotency are not fully defined. | Inconsistent client behavior and harder contract testing. | Define OpenAPI/HTTP contract, validation rules, and error mapping before or during implementation. | QS-7, Chapter 8 |
| **TD-4** | **Authentication/authorization not designed** | Explicitly out of scope for the course kata. | Cannot safely support real multi-user usage. | Add security ADR and API/auth design before production exposure. | R-5, Chapter 8 |
| **TD-5** | **Limited observability beyond AWS baseline** | Course scope favors minimal operations. | Harder diagnosis of latency/failure patterns in real use. | Add structured log fields, correlation IDs, dashboards/alarms, and optional tracing as needed. | Chapter 7, Chapter 8 |
| **TD-6** | **Numeric precision/currency rounding rules not specified** | Valuation correctness requires clear rules, but kata scope leaves detail open. | Inconsistent or incorrect money/asset calculations. | Define domain numeric type and rounding rules (e.g., decimal precision, per-currency rounding) and cover with tests. | QS-1, Chapter 8 |
