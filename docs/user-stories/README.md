# User Stories: Inventory and Pareto Progress

This directory contains testable user stories derived from the architecture in `architecture/` (arc42 Chapters 1-12 and the PlantUML sources in `architecture/diagrams/`). Bundles are written one at a time and each requires approval before the next is started.

## Domains and components extracted from the architecture

- **Bounded context:** the architecture defines a *single* bounded context, **Wallet Valuation**, because one ubiquitous language applies to wallet storage and valuation (Chapter 4, section 4.2; Chapter 8, section 8.2; Chapter 12, "Bounded Context"). The prefixes **WALLET**, **VALUATION** and **RATE** are story groupings (subdomains of the kata), not separate bounded contexts.
- **Containers (Chapter 5, section 5.1; Chapter 7, section 7.1):** Wallet HTTP API (API Gateway HTTP API), Wallet Function (AWS Lambda, Python 3.12), Wallet Table (DynamoDB on-demand), and the external Exchange Rate Provider (outside the system boundary).
- **Components inside the Wallet Function (Chapter 5, section 5.2):** Wallet API Handler, Wallet Application Service, Valuation Domain Service, `WalletRepository` port with its DynamoDB adapter, and `RateProvider` port with its Exchange Rate Provider Adapter. The ports keep domain rules independent of AWS and provider payloads (ADR-002).

## Pareto analysis (20% core ≈ 80% value)

Core stories are those needed for the minimum end-to-end capability, those that block other stories, those delivering the most user value, and those exercising the most architecture components.

The system is very small: 10 stories in total. A literal 20% (2 stories) would leave the end-to-end happy path incomplete — a populated wallet plus a valuation request still cannot produce a correct total without the rate-provider integration (FR-3, QS-1). Therefore **3 of 10 (30%)** are core: the "a few more than 20%" case allowed for a small system. The remaining 70% are Supporting; they harden failure paths, add CRUD breadth, and cover replaceability/caching rather than creating the primary value.

| ID | Short story | Architecture source | Priority |
|---|---|---|---|
| WALLET-STORY-001 | Add a stock | FR-1; Chapter 5, section 5.2; Chapter 8, sections 8.3 and 8.5 | Core (Pareto 20%) |
| VALUATION-STORY-001 | See the total value in a chosen currency | FR-2; Chapter 6, section 6.1; Chapter 5, section 5.2; QS-1 | Core (Pareto 20%) |
| RATE-STORY-001 | Value uses exchange rates from the external provider | FR-3; Chapter 5, section 5.2 (RateProvider port/adapter); Chapter 8, section 8.4; ADR-001; TC-5 | Core (Pareto 20%) |
| VALUATION-STORY-002 | Clear error instead of a partial value | ADR-004; Chapter 6, section 6.2; Chapter 8, section 8.3; QS-2 | Supporting |
| WALLET-STORY-002 | View wallet | FR-1, FR-4; Chapter 3, section 3.2 (I-1); Chapter 5, section 5.2; Chapter 8, section 8.5 | Supporting |
| WALLET-STORY-003 | Change or remove a stock | FR-1; Chapter 5, section 5.2 (update wallet use case); Chapter 8, section 8.5 | Supporting |
| WALLET-STORY-004 | Invalid input rejected | Chapter 8, section 8.3 (Validation); QS-7; TD-3 | Supporting |
| VALUATION-STORY-003 | Unsupported currency or stock type | Chapter 8, sections 8.1 and 8.3; QS-8; R-2 | Supporting |
| RATE-STORY-002 | Replace the rate provider | ADR-002; Chapter 8, section 8.4; QS-4; TC-5 | Supporting |
| RATE-STORY-003 | Cache exchange rates | ADR-004 (consequences); Chapter 8, section 8.4; R-1, R-4; TD-1 | Supporting |

## Story inventory and status

Status changes to **Written** only after the user approves the bundle. WALLET-STORY-001 was supplied by the user and is already written in `wallet.md`.

| ID | Title | Priority | Status |
|---|---|---|---|
| WALLET-STORY-001 | Add a stock to the wallet | Core (Pareto 20%) | Written |
| VALUATION-STORY-001 | See the total wallet value in a chosen currency | Core (Pareto 20%) | Written |
| RATE-STORY-001 | Value uses exchange rates from the external provider | Core (Pareto 20%) | Written |
| VALUATION-STORY-002 | Clear error instead of a partial value | Supporting | Pending |
| WALLET-STORY-002 | View wallet | Supporting | Pending |
| WALLET-STORY-003 | Change or remove a stock | Supporting | Pending |
| WALLET-STORY-004 | Invalid input rejected | Supporting | Pending |
| VALUATION-STORY-003 | Unsupported currency or stock type | Supporting | Pending |
| RATE-STORY-002 | Replace the rate provider | Supporting | Pending |
| RATE-STORY-003 | Cache exchange rates | Supporting | Pending |

**Pareto Progress: 3/3 core stories written (100%)**

Bundles live in one file per domain: `wallet.md` (existing, user-owned), `valuation.md`, `rate.md`.
