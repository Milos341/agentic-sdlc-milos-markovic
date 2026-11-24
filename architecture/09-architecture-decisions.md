# 9. Architecture Decisions

## ADR-001: Use Python on AWS Serverless with DynamoDB

**Status:** Accepted

**Context:**
The Wallet Valuation System stores wallets made of stocks (a quantity and a
stock type) and computes the total value of a wallet in a chosen currency.
Exchange rates come from an external provider. Traffic is low and variable,
the project is a course exercise, and cost and operational effort must stay
minimal.

**Decision:**
- Language: Python 3.12
- Compute: AWS Lambda behind an API Gateway HTTP API
- Data storage: Amazon DynamoDB with on-demand billing
- Infrastructure as Code: AWS SAM
- Exchange rates: accessed only through a rate provider interface (adapter),
  so the concrete provider can be chosen and replaced later

**Rationale:**
- Serverless scales to zero, so there is no cost when nobody uses the system
- Python 3.12 is already the project language and matches the existing
  tooling (black, isort, ruff, bandit)
- DynamoDB needs no servers or connection pooling and fits the Lambda model
- SAM is the deployment tool used in the CI/CD module of the course
- The rate provider interface isolates the only external dependency and makes
  the valuation logic easy to test with a fake provider

**Consequences:**
- DynamoDB access patterns must be designed upfront and queries are less
  flexible than SQL
- Lambda cold starts add latency to the first request after idle time
- The external rate provider is a risk: its availability and terms are outside
  our control, so caching and error handling must be decided later

## ADR-002: Apply Ports and Adapters for Domain Isolation

**Status:** Accepted

**Context:**
The core business capability is wallet valuation using domain rules. The system
must integrate with AWS-specific infrastructure (API Gateway/Lambda, DynamoDB)
and an external exchange-rate provider, while remaining testable and evolvable
(Quality Goals 1, 2, 5). The rate provider is explicitly an external dependency
that may change.

**Decision:**
- Structure the Wallet Function with ports-and-adapters (hexagonal) boundaries.
- Define domain-owned ports for external concerns, at minimum `WalletRepository`
  and `RateProvider`.
- Implement infrastructure adapters for DynamoDB and the external exchange-rate
  provider.
- Keep domain valuation rules independent of AWS SDK types, HTTP provider
  payloads, and API Gateway event formats.

**Rationale:**
- Domain logic can be unit-tested with fake ports, supporting correctness and
  fast feedback.
- Replacing the exchange-rate provider requires a new adapter, not changes to
  valuation rules.
- Infrastructure details (DynamoDB item schema, provider REST format) are
  isolated at the edges, reducing coupling.

**Consequences:**
- The codebase has more interfaces and mapping code than a direct implementation.
- Developers must maintain clear boundaries and avoid leaking infrastructure
  types into the domain.
- Adapter contracts need tests to ensure correct translation and error mapping.

## ADR-003: Keep a Single Wallet Function for the Initial Scope

**Status:** Accepted

**Context:**
The Wallet kata has a small scope: manage wallet stocks and calculate wallet
value in a chosen currency. The system is a course exercise with low traffic and
low operational complexity tolerance. Splitting use cases into multiple Lambda
functions or services would add deployment and coordination overhead.

**Decision:**
- Implement wallet management and valuation in a single deployable AWS Lambda
  container/function for the initial scope.
- Keep internal modular boundaries (handler, application service, domain,
  adapters) so the function can be split later if needed.

**Rationale:**
- A single function minimizes SAM resources, IAM wiring, and deployment
  complexity.
- The current use cases share the same bounded context and domain model.
- Internal modularity preserves an evolution path without paying premature
  microservice/serverless-function fragmentation costs.

**Consequences:**
- The function may grow if many new use cases are added; periodic review is
  needed to avoid a large, hard-to-maintain deployment unit.
- Independent scaling or release of wallet management versus valuation is not
  available in the initial design.
- A future split would require new SAM resources and interface/deployment
  decisions.

## ADR-004: Fail Explicitly on Exchange-Rate Unavailability

**Status:** Accepted

**Context:**
Wallet valuation depends on exchange rates from an external provider. The
provider can be unavailable, slow, rate-limited, or return errors. Returning a
partial or estimated valuation could produce incorrect business results and
undermine Quality Goal 1 (Correctness).

**Decision:**
- If required exchange-rate data cannot be obtained or validated, the valuation
  use case fails explicitly.
- The Exchange Rate Provider Adapter maps provider/transport failures to explicit
  application/domain-relevant errors.
- The API returns a clear error response indicating valuation is unavailable; it
  must not return a partial or silently incorrect total.
- Timeout, retry, circuit-breaker, and caching strategies are deferred as
  follow-up decisions.

**Rationale:**
- Correctness is prioritized over availability of a potentially wrong answer.
- Explicit error mapping makes failures diagnosable and keeps provider-specific
  details at the adapter boundary.
- Deferring resilience policies keeps the initial scope small while making the
  risk visible.

**Consequences:**
- Valuation requests can fail when the external provider is degraded, reducing
  availability from the user's perspective.
- Clients must handle valuation-unavailable errors.
- Follow-up ADRs or technical-debt items are needed for timeout/retry/caching
  behavior before production hardening.
