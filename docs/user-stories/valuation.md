# VALUATION Domain: Story Bundles

## VALUATION-STORY-001: See the total wallet value in a chosen currency

**AS A** investor
**I WANT** to request the total value of my wallet in a currency I choose
**SO THAT** I can understand what my holdings are worth in that currency

**Priority:** Core (Pareto 20%)

**Architecture references:**
- Chapter 1, FR-2 (Value wallet in a chosen currency), FR-4 (Expose API access) and Quality Goal 1 (Correctness)
- Chapter 5, section 5.2 (Wallet Application Service, Valuation Domain Service, RateProvider port) and section 5.1 (Wallet HTTP API, Wallet Function)
- Chapter 6, section 6.1 (Calculate Wallet Value in a Chosen Currency; runtime steps 1-10) and `diagrams/sequence-wallet-valuation.puml`
- Chapter 8, section 8.1 (Quantity, Currency, Exchange rate, Valuation) and section 8.3 (validation at the API boundary)
- Chapter 10, QS-1 (accurate valuation calculation) and ADR-002 (domain isolation behind ports)

### VALUATION-STORY-001-S1: Correct total from quantities and exchange rates

**GIVEN**
* I have a wallet containing 2 stocks of type "bitcoin" and 3 stocks of type "petroleum"
* A fake rate provider supplies 100 USD per bitcoin and 2 USD per petroleum

**WHEN**
* I request the value of my wallet in USD

**THEN**
* The response contains a total value of 206 USD (2 × 100 + 3 × 2)
* The response states that the currency of the total is USD

### VALUATION-STORY-001-S2: The investor's chosen currency is used

**GIVEN**
* I have a wallet containing 2 stocks of type "bitcoin" and 3 stocks of type "petroleum"
* Rates are available for both USD and EUR

**WHEN**
* I request the value of the same wallet in EUR instead of USD

**THEN**
* The total is computed from the rates to EUR, not the rates to USD
* The response contains a total expressed in EUR and states that the currency is EUR

> **Open question:** What numeric type and rounding rule must be used for the total (for example decimal precision or per-currency rounding)? The architecture leaves this open (TD-6, QS-1).
>
> **Open question:** How is a stock type that equals the target currency (for example "dollars" valued in USD) treated — as an identity conversion or as a rate lookup? The architecture does not decide this (Chapter 8, sections 8.1 and 8.4).
>
> **Open question:** What is the result of valuing an empty wallet (a zero total or an error)? The architecture does not decide this.

---

### Frontend sub-stories

Not applicable. The user interface is out of scope (Chapter 1, scope notes; Chapter 3, business scope). The system is an HTTP API; the investor requests a valuation over HTTPS/JSON (Chapter 3, section 3.2, I-1).

---

### Backend sub-stories

#### VALUATION-BE-001.1: HTTP endpoint to request a wallet valuation

**Parent:** VALUATION-STORY-001
**Architecture references:** Chapter 5, section 5.2 (Wallet API Handler); Chapter 6, section 6.1 (runtime steps 1-3 and 10); Chapter 8, section 8.3 (validation, not-found mapping); QS-7
**Note:** Route and request/response schema are defined in the API contract (TD-3).

##### VALUATION-BE-001.1-S1: Valid valuation request

**GIVEN**
* The Wallet API Handler receives a valuation request with a wallet identifier and target currency "USD"

**WHEN**
* The handler processes the request

**THEN**
* The "calculate wallet value" use case is called with the wallet identifier and target currency "USD"
* The handler returns a success response containing the total value and the currency "USD"

##### VALUATION-BE-001.1-S2: Missing target currency is rejected

**GIVEN**
* The Wallet API Handler receives a valuation request without a target currency

**WHEN**
* The handler processes the request

**THEN**
* The handler returns a 4xx validation error with a descriptive message
* The "calculate wallet value" use case is not called
* The error response contains no stack trace or internal details

##### VALUATION-BE-001.1-S3: Unknown wallet is mapped to not found

**GIVEN**
* The "calculate wallet value" use case returns a not-found result for the requested wallet identifier

**WHEN**
* The handler maps the use case result to HTTP

**THEN**
* The client receives an HTTP 404 (or the equivalent contract error defined in TD-3)
* No total valuation value is returned

#### VALUATION-BE-001.2: Calculate wallet value use case

**Parent:** VALUATION-STORY-001
**Architecture references:** Chapter 5, section 5.2 (Wallet Application Service); Chapter 6, section 6.1 (runtime steps 3-7); Chapter 8, section 8.5 (wallet loaded through the repository); ADR-002

##### VALUATION-BE-001.2-S1: Wallet is loaded and valued in the requested currency

**GIVEN**
* A fake WalletRepository holds a wallet with 2 "bitcoin" and 3 "petroleum"
* A fake RateProvider returns 100 USD per bitcoin and 2 USD per petroleum

**WHEN**
* The use case calculates the wallet value in USD

**THEN**
* The repository is asked to load the wallet by its identifier
* The Valuation Domain Service is asked to value the loaded wallet in USD
* The use case result contains the total 206 and the currency USD

##### VALUATION-BE-001.2-S2: Target currency is passed through unchanged

**GIVEN**
* A fake WalletRepository holds a wallet with 2 "bitcoin" and 3 "petroleum"
* A fake RateProvider returns 90 EUR per bitcoin and 2 EUR per petroleum

**WHEN**
* The use case calculates the wallet value in EUR

**THEN**
* The Valuation Domain Service is called with target currency EUR
* The use case result contains the total 186 and the currency EUR

##### VALUATION-BE-001.2-S3: No valuation is attempted for a missing wallet

**GIVEN**
* A fake WalletRepository holds no wallet with the requested identifier

**WHEN**
* The use case calculates the wallet value in USD

**THEN**
* A not-found use case result is returned
* The Valuation Domain Service is not called

#### VALUATION-BE-001.3: Domain valuation rules with a fake rate provider

**Parent:** VALUATION-STORY-001
**Architecture references:** Chapter 5, section 5.2 (Valuation Domain Service, RateProvider port); Chapter 6, section 6.1 (runtime steps 7-9); Chapter 8, section 8.1 (Valuation, Exchange rate); QS-1; QS-3; ADR-002

##### VALUATION-BE-001.3-S1: Each stock is converted and the results are summed

**GIVEN**
* A wallet holds 2 "bitcoin" and 3 "petroleum"
* A fake RateProvider returns 100 USD for bitcoin to USD and 2 USD for petroleum to USD

**WHEN**
* The Valuation Domain Service computes the total wallet value in USD

**THEN**
* The rate provider is asked for the bitcoin-to-USD and petroleum-to-USD rates
* The returned total is 206 with currency USD

##### VALUATION-BE-001.3-S2: Rates are requested per stock type, not per unit

**GIVEN**
* A wallet holds 2 "bitcoin" and 3 "petroleum"
* A fake RateProvider returns a rate for each requested stock type to USD

**WHEN**
* The Valuation Domain Service computes the total wallet value in USD

**THEN**
* Exactly two rate lookups are made: bitcoin to USD and petroleum to USD
* The total equals 2 × the bitcoin rate plus 3 × the petroleum rate

##### VALUATION-BE-001.3-S3: Valuation rules are unit-testable without infrastructure

**GIVEN**
* The Valuation Domain Service is configured with a fake RateProvider
* No AWS services and no external HTTP provider are available

**WHEN**
* The valuation unit tests are run

**THEN**
* The domain rules execute directly through the RateProvider port
* Normal and failure cases are covered without network or cloud dependencies

---

### Infrastructure sub-stories

#### VALUATION-INFRA-001.1: Deploy the valuation route and the Wallet Function

**Parent:** VALUATION-STORY-001
**Architecture references:** Chapter 7, sections 7.2 and 7.3; ADR-001; ADR-003; TC-4

##### VALUATION-INFRA-001.1-S1: Deployment with SAM

**GIVEN**
* The AWS SAM template defines an HTTP API route for valuation integrated with the Wallet Function

**WHEN**
* A developer runs `sam build` and `sam deploy`

**THEN**
* The valuation endpoint is reachable over HTTPS
* The Wallet Function runs on Python 3.12
* The function's environment configuration supplies the Wallet Table name and the rate provider endpoint/settings
* The function's execution role has least-privilege access to the Wallet Table only

#### VALUATION-INFRA-001.2: Data store for wallet reads during valuation

**Parent:** VALUATION-STORY-001
**Architecture references:** Chapter 7, section 7.2 (Wallet Table); Chapter 8, section 8.5 (Persistence); TC-3; TD-2

##### VALUATION-INFRA-001.2-S1: Wallet aggregate is read from the Wallet Table

**GIVEN**
* The AWS SAM template provisions the Wallet Table with on-demand billing
* The AWS SDK is mocked in the adapter test

**WHEN**
* A valuation request loads a wallet through the DynamoDB Wallet Repository

**THEN**
* The repository reads the wallet items from the Wallet Table through the DynamoDB API over HTTPS
* The loaded wallet contains the stocks to be valued
* No provisioned database capacity needs to be managed

#### VALUATION-INFRA-001.3: Event handling

Not applicable. The valuation flow is synchronous request and response (Chapter 4, section 4.2; Chapter 6, section 6.1). The outbound exchange-rate call is a synchronous HTTPS/REST integration, not an event (Chapter 5, section 5.1).

#### VALUATION-INFRA-001.4: Monitoring and observability

**Parent:** VALUATION-STORY-001
**Architecture references:** Chapter 7, section 7.3 (Observability); Chapter 8, section 8.7 (Logging, Observability, and Diagnostics)

##### VALUATION-INFRA-001.4-S1: Logs and metrics are available for valuation requests

**GIVEN**
* The stack is deployed

**WHEN**
* A valuation request is processed

**THEN**
* The Lambda invocation is logged to CloudWatch Logs with structured fields including the use case name and a request correlation identifier where available
* API Gateway and Lambda metrics (requests, errors, duration) are available
* The logs contain no secrets or credentials
