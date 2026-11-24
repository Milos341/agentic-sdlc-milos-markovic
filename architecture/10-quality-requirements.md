# 10. Quality Requirements

This chapter captures quality requirements as a quality tree and concrete scenarios. It refines the quality goals introduced in Chapter 1 and makes them verifiable.

## 10.1 Quality Tree

| Quality category | Priority | Refinement | Scenario ref |
|---|---|---|---|
| **Correctness** | 1 | Accurate valuation calculation | QS-1 |
|  |  | No partial or estimated result on missing rate data | QS-2 |
| **Testability / Replaceability** | 2 | Domain logic testable with fakes | QS-3 |
|  |  | Exchange-rate provider replaceable via adapter | QS-4 |
| **Low operational cost & effort** | 3 | Scale to zero when idle | QS-5 |
|  |  | Simple, reproducible deployment | QS-6 |
| **Reliability** | 4 | Explicit failure on external dependency outage | QS-2 |
|  |  | Clear client-facing error on failure | QS-7 |
| **Evolvability** | 5 | Add stock type or currency with localized change | QS-8 |
|  |  | Replace external rate provider without domain changes | QS-4 |

## 10.2 Quality Scenarios

| ID | Quality attribute | Stimulus | Environment | Artifact / Flow | Response | Measure / Acceptance |
|---|---|---|---|---|---|---|
| **QS-1** | Correctness | An investor requests valuation of a wallet containing known stock quantities and types in a chosen currency. | Normal operation; exchange rates available from a fake or real provider. | Wallet Application Service + Valuation Domain Service | System computes the total by converting each stock using the applicable exchange rate and summing results. | For a deterministic test input, the returned total equals the expected arithmetic result exactly (within the defined numeric precision/currency rounding rule). |
| **QS-2** | Correctness, Reliability | An exchange rate required for valuation is unavailable, times out, or returns an invalid response. | External Exchange Rate Provider degraded/unavailable. | Exchange Rate Provider Adapter -> Valuation use case -> API Handler | System fails explicitly and returns a clear valuation-unavailable error. | Response contains no total valuation value; no partial/estimated total is persisted or returned; error is logged with diagnostic context. |
| **QS-3** | Testability | A developer runs unit tests for valuation logic. | Local test environment, no AWS, no external HTTP provider. | Valuation Domain Service with fake `RateProvider` and fake/in-memory `WalletRepository` | Tests execute domain rules directly through ports. | Valuation unit tests run without network/cloud dependencies and cover normal and failure cases. |
| **QS-4** | Replaceability, Evolvability | A new exchange-rate provider must be integrated or an existing one replaced. | Development/change scenario. | `RateProvider` port + new Exchange Rate Provider Adapter | Developer adds/changes adapter and configuration; domain valuation rules remain unchanged. | No modifications required in Valuation Domain Service for provider replacement; adapter contract tests pass. |
| **QS-5** | Low operational cost | No investor requests are made for an extended period. | Deployed single-stage course environment. | API Gateway + Lambda + DynamoDB on-demand | System remains deployed but consumes no always-on compute capacity. | No continuously running EC2/container/server process is required; compute cost is usage-based (Lambda invocations/duration). |
| **QS-6** | Low operational effort | A developer deploys the system to the course environment. | Developer machine with AWS credentials and SAM tooling. | AWS SAM template | SAM builds and deploys the API, function, and table as one stack. | Deployment uses documented `sam build` and `sam deploy` flow; no manual per-resource console setup required for core resources. |
| **QS-7** | Reliability, Usability | A client sends an invalid request (e.g., missing target currency or invalid quantity). | Normal operation. | Wallet API Handler | System rejects the request before valuation/persistence side effects. | Client receives a clear 4xx validation error; response does not expose internal stack traces or secrets. |
| **QS-8** | Evolvability | A new stock type or currency is added to supported valuation inputs. | Development/change scenario. | Domain model, validation, rate-provider adapter mapping | Changes are made in domain/adapter mapping and corresponding tests. | Adding support does not require changes to unrelated infrastructure concerns beyond necessary configuration/mapping; existing valuation tests remain green. |
