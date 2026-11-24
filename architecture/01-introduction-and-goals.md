# 1. Introduction and Goals

This chapter describes the key requirements, quality goals, and stakeholders for the **Wallet Valuation System**. It provides the context needed to understand the architectural decisions documented in the following chapters.

## 1.1 Requirements Overview

The Wallet Valuation System is a course exercise (Wallet kata) that manages a wallet of stocks and computes its total value in a user-selected currency.

### Key Functional Requirements

| ID | Requirement | Description |
|---|---|---|
| FR-1 | Manage wallet stocks | The system stores a wallet containing stocks. Each stock entry consists of a **quantity** and a **stock type** (for example: petroleum, euros, bitcoins, dollars). |
| FR-2 | Value wallet in a chosen currency | The system computes the total value of the wallet in a currency chosen by the user (for example: USD, EUR). |
| FR-3 | Use external exchange rates | Currency/stock conversion uses exchange rates obtained from an external rate provider. The valuation logic depends on a **rate provider interface**, not a concrete external service. |
| FR-4 | Expose API access | The system exposes its capabilities through an HTTP API, allowing an investor to manage wallet data and request valuations. |

### Scope Notes

- The system is intentionally small and focused on the kata's domain: wallet storage and valuation.
- Authentication, user account management, and UI are out of scope unless added in later decisions.
- The concrete exchange-rate provider is not fixed by the architecture; it is integrated behind an adapter/interface.

## 1.2 Quality Goals

The following quality goals have the highest priority for architectural decisions.

| Priority | Quality Goal | Motivation | Scenario |
|---|---|---:|---|
| 1 | **Correctness** | A wrong wallet valuation undermines the system's purpose. | Given a wallet and known exchange rates, the computed total in the target currency matches the expected arithmetic result. |
| 2 | **Testability / Replaceability** | The external rate provider is outside our control and must not block automated testing. | Valuation logic can be tested with a fake rate provider; swapping the concrete provider requires only adapter changes. |
| 3 | **Low operational cost & effort** | The project is a course exercise with low, variable traffic. | When idle, the system incurs no compute cost; deployment and infrastructure remain simple to operate. |
| 4 | **Reliability under external dependency failure** | Exchange-rate providers can be unavailable or slow. | When the rate provider fails, the system returns a clear error and does not produce partial or incorrect valuations. |
| 5 | **Evolvability** | The kata may grow with new stock types, currencies, or providers. | Adding a new stock type or rate provider adapter does not require changes to core valuation rules. |

## 1.3 Stakeholders

| Role | Representative | Expectations |
|---|---|---|
| Investor / API User | End user of the Wallet API | Can store wallet stocks and obtain a correct total value in a chosen currency through a simple API. |
| Developer / Maintainer | Course project developer | Clear architecture, testable design, simple local reasoning, and alignment with project tooling (Python 3.12, lint/test tools). |
| Course Instructor / Evaluator | SDLC course staff | Architecture documentation follows arc42/C4 expectations, decisions are justified, and the design demonstrates good engineering practices. |
| Operations / Deployer | Developer using AWS SAM | Simple deployment, minimal infrastructure management, predictable cost, and observable failures. |
| External Rate Provider | Third-party service/operator | Receives rate lookup requests over HTTPS/REST; availability, terms, and response format are external constraints. |

## 1.4 Related Artifacts

- **System context diagram:** `architecture/diagrams/c4-context.puml` (and generated `c4-context.svg`)
- **Initial technology decision:** `architecture/09-architecture-decisions.md` — ADR-001
- **Architecture documentation structure:** arc42 chapters in `architecture/`
