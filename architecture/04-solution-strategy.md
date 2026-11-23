# 4. Solution Strategy

This chapter summarizes the fundamental decisions and strategies that shape the architecture of the **Wallet Valuation System**. It provides a compact bridge between the goals and constraints (Chapters 1-2) and the detailed views that follow.

## 4.1 Technology Decisions

The core technology choices are established in [ADR-001](09-architecture-decisions.md#adr-001-use-python-on-aws-serverless-with-dynamodb). The table below summarizes how they support the solution.

| Decision | Strategy | Related goals / constraints |
|---|---|---|
| **Python 3.12** | Implement domain logic, Lambda handlers, and tests in Python 3.12, using the repository's existing quality tooling (black, isort, ruff, bandit). | TC-1, CV-1, maintainability for course developers |
| **AWS Lambda behind API Gateway HTTP API** | Expose wallet and valuation capabilities as stateless HTTP endpoints. Each request is handled by Lambda functions; no always-on server is required. | TC-2, TC-6, low operational cost/effort |
| **Amazon DynamoDB (on-demand)** | Persist wallet data in a managed NoSQL store with on-demand billing. Access patterns are designed around wallet read/write and valuation use cases. | TC-3, low operational cost/effort |
| **AWS SAM** | Define infrastructure as code and deploy the API, functions, and database as a single SAM-managed stack. | TC-4, simple deployment |
| **Rate provider interface/adapter** | Keep exchange-rate lookup behind an internal `RateProvider` interface. The external provider is an adapter at the infrastructure boundary; domain logic depends only on the interface. | TC-5, FR-3, testability/replaceability, reliability under dependency failure |

## 4.2 Top-level Decomposition

The system is intentionally small. It is modeled as a single bounded context, **Wallet Valuation**, because the same ubiquitous language applies across wallet storage and valuation (wallet, stock, stock type, quantity, currency, exchange rate, valuation). Internally, the solution is decomposed into clear responsibilities:

| Part | Responsibility | Key elements |
|---|---|---|
| **API / Interface layer** | Accept HTTPS requests, validate input, map HTTP concerns to application use cases, and return responses/errors. | API Gateway routes, Lambda handlers, request/response DTOs |
| **Application layer** | Orchestrate use cases without containing core valuation rules. | Use cases such as create/update/get wallet and calculate wallet value in target currency |
| **Domain layer** | Contain the business model and valuation rules. This layer has no dependency on AWS, DynamoDB, or concrete HTTP providers. | Wallet, Stock, StockType/Quantity value objects, ValuationService/domain rules, `RateProvider` port |
| **Infrastructure / Adapter layer** | Implement technical concerns and external integrations. | DynamoDB wallet repository adapter, external exchange-rate provider adapter, SAM/IaC configuration |

This decomposition follows a ports-and-adapters (hexagonal) style inside the serverless boundary: Lambda handlers are entry adapters, DynamoDB and the exchange-rate provider are driven adapters, and the domain remains testable in isolation.

Event-driven communication is not used for the initial scope because no multiple services react to the same domain event. The current interactions are synchronous request/response flows, as shown in Chapter 3. If future capabilities introduce independent reactions to wallet or valuation events, they should use past-tense event names, idempotent consumers, and dead-letter queues, per the architectural principles.

## 4.3 Quality Goal Achievement

| Quality goal (Chapter 1) | Architectural approach |
|---|---|
| **Correctness** | Valuation rules are isolated in the domain layer and covered by unit tests using deterministic fake rate providers. Input validation occurs at the API boundary; domain invariants (e.g., valid quantity, known/handled stock types/currencies) are enforced in the model/use cases. |
| **Testability / Replaceability** | External dependencies are accessed through ports/interfaces (`RateProvider`, wallet repository). Tests use fakes/in-memory adapters; replacing a concrete exchange-rate provider requires only a new adapter and configuration, not domain changes. |
| **Low operational cost & effort** | Serverless-first stack (API Gateway + Lambda + DynamoDB on-demand) scales to zero when idle. AWS SAM keeps deployment declarative and simple for a course project. |
| **Reliability under external dependency failure** | The exchange-rate provider adapter isolates failures and translates them into explicit application errors. The system does not return partial or silently incorrect valuations. Timeouts, error mapping, and caching/fallback behavior are identified as follow-up decisions (see ADR-001 consequences and Chapter 11 risks). |
| **Evolvability** | Domain terminology and boundaries separate core valuation from infrastructure. New stock types, currencies, or rate providers are added through adapters/configuration and domain extensions, minimizing cross-cutting changes. |

## 4.4 Organizational Decisions

| Decision | Rationale |
|---|---|
| **arc42 + C4 documentation in `architecture/`** | Keeps architecture knowledge versioned with the code and understandable to developers and course evaluators (OC-2, OC-3). |
| **ADR discipline** | Significant decisions are recorded in Chapter 9 with Status, Context, Decision, Rationale, and Consequences; ADR-001 is preserved and future decisions are additive (OC-4, CV-5). |
| **Git workflow constraints** | Work starts from `main`, commit messages follow `#<issue> <type>(<scope>): <description>`, pre-commit hooks must pass, and changes flow through issues, pull requests, and review (OC-6 to OC-9). |
| **Incremental chapter review** | Each arc42 chapter is reviewed before proceeding, reducing rework and keeping the documentation aligned with stakeholder expectations (OC-10). |
