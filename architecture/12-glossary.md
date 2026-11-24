# 12. Glossary

This glossary defines key terms used in the Wallet Valuation System architecture documentation. Terms are aligned with the Wallet kata domain and the arc42/C4 documentation.

| Term | Definition |
|---|---|
| **Adapter** | An infrastructure component that implements a port and translates between domain/application interfaces and external technology (e.g., DynamoDB SDK, external HTTP provider). |
| **Amazon DynamoDB** | AWS managed NoSQL database used to store wallet data. In this architecture, it uses on-demand billing. |
| **API Gateway HTTP API** | AWS managed HTTP entry point that receives investor requests and invokes the Wallet Function. |
| **ADR (Architecture Decision Record)** | A short document capturing a significant architectural decision, including status, context, decision, rationale, and consequences. |
| **arc42** | A template for documenting software and system architectures, used to structure this `architecture/` documentation set. |
| **AWS SAM** | AWS Serverless Application Model; the Infrastructure-as-Code tool used to define and deploy the system's AWS resources. |
| **Bounded Context** | A DDD boundary within which a domain model and ubiquitous language are consistent. This system currently uses a single Wallet Valuation bounded context. |
| **C4 Model** | A diagramming approach for software architecture at Context, Container, Component, and Code levels. This documentation uses C4 Context, Container, Component, and Deployment views. |
| **Currency** | The target unit in which the total wallet value is expressed, such as USD or EUR. |
| **Domain Service** | Domain logic that performs a business operation not naturally owned by a single entity/value object; here, valuation calculation is performed by the Valuation Domain Service. |
| **Exchange Rate** | Conversion information used to translate a stock type/quantity into a target currency value. |
| **Exchange Rate Provider** | An external system that supplies exchange rates. The concrete provider is accessed through the `RateProvider` port/adapter. |
| **Investor** | The person or API client acting on their behalf who manages wallet stocks and requests wallet valuation. |
| **Lambda Proxy Integration** | API Gateway integration mode where the HTTP request is passed to Lambda as an event and the Lambda returns an HTTP response structure. |
| **Port** | A domain-owned interface that defines a capability needed by the application/domain (e.g., `WalletRepository`, `RateProvider`) without binding to a specific technology. |
| **Ports and Adapters (Hexagonal Architecture)** | An architectural style where core logic depends on ports, and external technologies implement adapters, isolating domain logic from infrastructure. |
| **Quantity** | The numeric amount of a stock type held in a wallet. |
| **RateProvider** | Domain-owned port used by valuation logic to obtain exchange rates from an external source. |
| **Stock** | A wallet entry consisting of a stock type and a quantity. |
| **Stock Type** | The kind/category of asset held in a wallet, such as petroleum, euros, bitcoins, or dollars. |
| **Valuation** | The computed total value of all stocks in a wallet, expressed in a chosen currency. |
| **Wallet** | The domain aggregate/container holding a collection of stocks. |
| **Wallet Function** | The AWS Lambda (Python 3.12) container that hosts API handling, application orchestration, domain valuation, and infrastructure adapters. |
| **Wallet HTTP API** | The public API Gateway HTTP API exposed by the system for wallet management and valuation requests. |
| **Wallet Table** | The DynamoDB table that persists wallet data and stock entries. |
| **WalletRepository** | Domain-owned port used by application/use-case logic to load and save wallets. |
