# 8. Cross-cutting Concepts

This chapter describes recurring concepts and patterns that apply across multiple building blocks of the **Wallet Valuation System**. The concepts are intentionally lightweight and appropriate for the course-exercise scope; where details are not yet decided, they are marked as follow-up decisions.

## 8.1 Domain Model and Ubiquitous Language

The system follows the Wallet kata domain language consistently (CV-2).

| Term | Meaning | Notes |
|---|---|---|
| **Wallet** | A collection of stock holdings owned/queried by the investor context. | Persisted in the Wallet Table; loaded as an aggregate for use cases. |
| **Stock** | A holding in the wallet, represented by a stock type and a quantity. | A wallet may contain multiple stocks of different types. |
| **Stock type** | The kind of asset held, such as petroleum, euros, bitcoins, or dollars. | Treated as a domain value; supported types/conversion rules must be defined consistently. |
| **Quantity** | The amount of a given stock type in the wallet. | Domain validation should reject invalid quantities (e.g., negative or non-numeric input) at the boundary/use case as appropriate. |
| **Currency** | The target unit for valuation output, e.g., USD or EUR. | Chosen by the investor in valuation requests. |
| **Exchange rate** | Conversion information from one stock type/currency to another. | Obtained from an external provider through the `RateProvider` port. |
| **Valuation** | The total value of all wallet stocks expressed in a chosen currency. | Computed by domain rules; must not be partial or estimated on provider failure. |

## 8.2 Architecture and Code Structure

| Concept | Approach | Rationale |
|---|---|---|
| **Ports and adapters** | Domain/application logic depends on ports (`WalletRepository`, `RateProvider`); infrastructure implements adapters (DynamoDB repository, external rate adapter). | Supports testability, replaceability, and isolation of external dependencies (ADR-001, TC-5, Quality Goals 2 and 5). |
| **Layering inside Wallet Function** | API handler -> application service -> domain service/ports; adapters at the infrastructure edge. | Keeps HTTP, AWS SDK, and provider-specific concerns out of domain valuation rules (Chapter 5). |
| **Single bounded context** | Wallet storage and valuation are modeled as one Wallet Valuation bounded context. | The kata scope is small and shares one ubiquitous language (Chapter 4). |
| **Stateless compute** | Lambda handlers are stateless; state lives in DynamoDB or is obtained per request from external services. | Required by Lambda execution model (TC-2) and simplifies scaling. |

## 8.3 Validation and Error Handling

### Validation

| Location | Responsibility |
|---|---|
| **API boundary (Wallet API Handler)** | Validate request shape, required fields, data types, and basic format (e.g., missing wallet identifier, invalid quantity format, missing target currency). Return clear client errors. |
| **Application/domain layer** | Enforce domain invariants and use-case rules (e.g., unknown/unsupported stock type handling, valuation preconditions). Do not rely only on API-layer checks. |
| **Adapters** | Validate/normalize external data before passing it into domain logic (e.g., provider response shape, missing rate). |

### Error Handling

| Scenario | Handling strategy | Result |
|---|---|---|
| **Invalid client request** | Reject at API boundary with a descriptive validation error. | No state change; client receives actionable HTTP 4xx response. |
| **Wallet not found** | Application returns a not-found use-case result. | Handler maps to HTTP 404 (or equivalent API contract error). |
| **Exchange rate unavailable / provider error / timeout** | Rate adapter maps technical failures to an explicit rate-provider/application error; valuation use case propagates failure. | No partial or incorrect valuation; handler returns clear HTTP 5xx/503-style error (exact contract is a later decision). |
| **Unexpected internal error** | Log error details internally; return generic error response to client. | Avoid leaking internal implementation details; preserve diagnosability through logs. |

**Rule:** The system never returns a partial valuation when required exchange-rate data is missing or unreliable.

## 8.4 External Integration Concept

The Exchange Rate Provider is the only external runtime dependency.

| Concept | Approach |
|---|---|
| **Interface-first integration** | Domain/application uses a `RateProvider` port. The concrete provider is an adapter implementing that port. |
| **Adapter responsibilities** | Build provider request, handle HTTPS/REST communication, interpret provider response, normalize rates to domain format, map errors/timeouts to explicit domain/application errors. |
| **Configuration** | Provider endpoint/credentials/timeouts are deployment configuration, not hard-coded domain logic. |
| **Resilience (follow-up)** | Timeout, retry, circuit breaker, and caching policies are not fixed by existing chapters/ADRs. They are follow-up decisions and tracked in Chapter 11 risks/technical debt. |

## 8.5 Persistence Concept

| Concept | Approach |
|---|---|
| **Database** | Amazon DynamoDB with on-demand billing (ADR-001, TC-3). |
| **Repository pattern** | `WalletRepository` port abstracts persistence; DynamoDB adapter encapsulates table names, keys, item schema, and SDK calls. |
| **Data model** | Wallet and stock entries are stored as DynamoDB items. Detailed key schema/access patterns are an implementation-level design decision to be finalized with the code; they must support wallet load/save by wallet identifier. |
| **Consistency** | Single-wallet read/write operations should use DynamoDB item operations appropriate to the chosen schema. Strong consistency requirements, if any, are a later decision. |
| **Idempotency** | Write operations exposed by the API should define idempotency behavior where relevant (e.g., create/update semantics); detailed API contract is a later decision. |

## 8.6 Security Concept

The kata scope is small; security is handled with minimal, explicit boundaries.

| Area | Current concept | Status / follow-up |
|---|---|---|
| **Transport security** | Investor-to-API and system-to-rate-provider communication use HTTPS/HTTPS-REST as defined by context constraints. | Established by TC-6 / Chapter 3. |
| **IAM least privilege** | Lambda execution role has least-privilege access to the Wallet Table only. | Established in Chapter 7. |
| **Secrets/configuration** | Provider credentials or API keys, if required by a chosen provider, must be injected as configuration/secrets, never embedded in code or domain logic. | Concrete secret store is a later decision. |
| **Authentication/authorization** | No user authentication/authorization model is defined by the kata. | Out of current scope; requires a future decision before production/multi-user use. |
| **Input handling** | Validate and sanitize external input at boundaries; avoid exposing internal stack traces in API responses. | Baseline requirement for API robustness. |

## 8.7 Logging, Observability, and Diagnostics

| Concept | Approach |
|---|---|
| **Structured logging** | Lambda functions emit structured logs (e.g., JSON fields) to CloudWatch Logs, including request correlation identifiers where available, use case name, and error category. |
| **Metrics** | Use baseline AWS metrics for API Gateway, Lambda, and DynamoDB (request count, latency, errors, throttles, duration). |
| **Tracing** | Distributed tracing (e.g., AWS X-Ray) is optional and can be added if operational visibility needs grow; not required by current scope. |
| **Sensitive data** | Logs must not contain secrets, credentials, or unnecessary personal data. Wallet/rate payloads should be logged carefully and minimized. |
| **Diagnosability** | Error logs should include enough context to diagnose provider failures, validation failures, and persistence failures without exposing sensitive internals to clients. |

## 8.8 Testing Concept

Testing is central because the valuation logic must be correct and external dependencies must be replaceable.

| Test level | Focus | Dependencies |
|---|---|---|
| **Unit tests** | Domain valuation rules, value objects, use-case behavior, error mapping. | Fake/in-memory `RateProvider` and `WalletRepository` implementations. |
| **Adapter tests** | DynamoDB repository mapping and rate adapter request/response/error translation. | Mocked AWS SDK/HTTP client; optional local integration tooling as a later decision. |
| **Contract/API tests** | HTTP request/response behavior, validation errors, valuation success/failure responses. | Lambda handler with fakes or local SAM invocation. |
| **End-to-end tests** | Full deployed path from API to DynamoDB and, where appropriate, a test double for the external rate provider. | Deployed single-stage environment; scope controlled for course cost/effort. |

## 8.9 Configuration and Deployment Concept

| Concept | Approach |
|---|---|
| **IaC** | AWS SAM defines and deploys the API, function, and table as a single stack (ADR-001, Chapter 7). |
| **Environment configuration** | Environment-specific values are provided through SAM/Lambda configuration and environment variables; no environment-specific logic in domain code. |
| **Single stage** | One environment/single stage is assumed for the course scope; additional environments are a later decision (Chapter 7). |
| **Build/deploy** | Use `sam build` and `sam deploy` as the baseline deployment flow. |
