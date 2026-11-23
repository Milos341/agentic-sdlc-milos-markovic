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
