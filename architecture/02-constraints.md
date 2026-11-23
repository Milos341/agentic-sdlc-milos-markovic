# 2. Architecture Constraints

This chapter lists constraints that limit architectural and implementation freedom for the Wallet Valuation System. Constraints are facts or decisions that the architecture must comply with; they are not quality goals.

## 2.1 Technical Constraints

| ID | Constraint | Background / Motivation |
|---|---|---|
| TC-1 | **Python 3.12** | The project language is Python 3.12, aligned with existing repository tooling (black, isort, ruff, bandit). Implementation and tests must be compatible with this runtime. |
| TC-2 | **AWS Lambda behind API Gateway HTTP API** | Compute is serverless on AWS Lambda, exposed through API Gateway. The design must fit the Lambda execution model (stateless handlers, cold starts, execution time/memory limits). |
| TC-3 | **Amazon DynamoDB with on-demand billing** | Wallet data is stored in DynamoDB using on-demand capacity. Data modeling must account for DynamoDB access patterns, key design, and limited query flexibility compared to SQL. |
| TC-4 | **AWS SAM for Infrastructure as Code** | Infrastructure is defined and deployed with AWS SAM, as required by the course CI/CD module. Deployment artifacts and resource definitions must be SAM-compatible. |
| TC-5 | **External exchange rates via interface/adapter** | Exchange rates are obtained from an external provider, but valuation logic must depend only on a rate provider interface. Concrete provider selection, API format, and authentication details are isolated behind an adapter. |
| TC-6 | **HTTP/REST integration boundaries** | The C4 system context diagram (`architecture/diagrams/c4-context.puml`) defines the communication boundaries: the investor calls the Wallet Valuation System over HTTPS, and the system calls the External Exchange Rate Provider over HTTPS/REST. |

## 2.2 Organizational / Process Constraints

| ID | Constraint | Background / Motivation |
|---|---|---|
| OC-1 | **Course exercise scope** | The Wallet kata is a course project. Scope, complexity, and operational effort must remain appropriate for an educational exercise. |
| OC-2 | **arc42 + C4 documentation** | Architecture documentation must follow the arc42 template and use C4 model notation for architecture diagrams, as required by the architecture workflow. |
| OC-3 | **Architecture artifacts in repository** | Documentation lives under `architecture/`, with one file per arc42 chapter and PlantUML diagrams under `architecture/diagrams/`. Existing user-owned artifacts (`c4-context.puml`, ADR-001) must not be overwritten. |
| OC-4 | **ADR discipline** | Significant architectural decisions are recorded as ADRs in Chapter 9 using Status, Context, Decision, Rationale, and Consequences. ADR-001 remains unchanged; new decisions are added as ADR-002+. |
| OC-5 | **PlantUML diagram workflow** | `.puml` files follow the project C4 PlantUML conventions: `@startuml <filename-without-extension>` first line, built-in `!include <C4/...>` library, elements with name/description/technology where applicable, and `Rel` labels with protocol. SVGs are generated/staged by the pre-commit hook, not created manually. |
| OC-6 | **Branches created from `main`** | All work branches are created from the `main` branch, keeping the integration baseline clear and consistent. |
| OC-7 | **Commit message format** | Commit messages must follow the format `#<issue> <type>(<scope>): <description>`, linking changes to an issue and making change intent explicit. |
| OC-8 | **Pre-commit hooks must pass** | Pre-commit hooks are mandatory quality gates. Changes must pass all configured hooks before they can be committed. |
| OC-9 | **Issue, pull request, and review process** | Work is tracked through issues; changes are proposed through pull requests and must go through the review process before integration. |
| OC-10 | **Incremental review** | Chapters are produced one at a time and require user approval before proceeding, reducing rework and keeping documentation aligned with expectations. |

## 2.3 Conventions

| ID | Convention | Background / Motivation |
|---|---|---|
| CV-1 | **Python code quality tooling** | The repository uses Python quality tools (black, isort, ruff, bandit) as indicated by ADR-001. New Python code should conform to these checks. |
| CV-2 | **Domain terminology** | Use the kata/domain terms consistently: *wallet*, *stock*, *stock type*, *quantity*, *currency*, *exchange rate*, *valuation*. Avoid mixing synonymous terms without definition. |
| CV-3 | **Interface at external boundary** | External dependencies, especially the exchange-rate provider, are accessed through interfaces/adapters to support replacement and fake implementations in tests. |
| CV-4 | **Diagrams as code** | Architecture diagrams are maintained as PlantUML source files in version control; generated SVGs are derived artifacts. |
| CV-5 | **Explicit decision rationale** | Documentation captures why decisions were made (ADRs, constraints, tradeoffs), not only the resulting structure. |
