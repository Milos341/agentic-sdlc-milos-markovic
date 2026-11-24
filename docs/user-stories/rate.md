# RATE Domain: Story Bundles

## RATE-STORY-001: Value uses exchange rates from the external provider

**AS A** investor
**I WANT** my wallet to be valued with exchange rates obtained from the external rate provider
**SO THAT** the total reflects real conversion data instead of invented or hard-coded rates

**Priority:** Core (Pareto 20%)

**Architecture references:**
- Chapter 1, FR-3 (Use external exchange rates), Quality Goal 2 (Testability / Replaceability) and Quality Goal 4 (Reliability under external dependency failure)
- Chapter 3, section 3.2, I-2 (Wallet Valuation System ↔ Exchange Rate Provider); TC-5; TC-6
- Chapter 5, section 5.1 (Exchange Rate Provider container and key interfaces) and section 5.2 (RateProvider port, Exchange Rate Provider Adapter)
- Chapter 6, section 6.1 (Calculate Wallet Value in a Chosen Currency, runtime steps 7-9) and `diagrams/sequence-wallet-valuation.puml`
- Chapter 8, section 8.4 (External Integration Concept) and section 8.1 (Exchange rate)
- Chapter 10, QS-1 and QS-3; ADR-001; ADR-002; R-2

### RATE-STORY-001-S1: Valuation uses a rate from the external provider

**GIVEN**
* I have a wallet containing 2 stocks of type "bitcoin"
* The configured external rate provider supplies a bitcoin-to-USD rate of 100

**WHEN**
* I request the value of my wallet in USD

**THEN**
* The system requests the bitcoin-to-USD rate from the external provider over HTTPS/REST
* The response contains a total of 200 USD, computed with the rate supplied by the provider

### RATE-STORY-001-S2: Valuation logic works against a fake rate provider

**GIVEN**
* The valuation logic is wired to a fake RateProvider that supplies a bitcoin-to-USD rate of 100
* I have a wallet containing 2 stocks of type "bitcoin"

**WHEN**
* I request the value of my wallet in USD

**THEN**
* The total of 200 USD is computed from the fake provider's rate
* No call is made to the external provider, because the domain sees only the RateProvider port

> **Open question:** Which concrete provider, endpoint, API payload format and authentication mechanism are used? The architecture deliberately leaves these open behind the adapter (Chapter 1, scope notes; Chapter 3, section 3.2, I-2; TC-5).
>
> **Open question:** Does the provider return a per-unit exchange rate that the domain multiplies by quantity, or an already-converted value? Chapter 3, I-2 permits quantity/context in the request, while Chapter 6, section 6.1 describes the domain computing the total from rates; the choice is not fixed.
>
> **Open question:** What timeout, retry and caching policy applies to provider calls? These are deferred follow-up decisions (ADR-004 consequences; Chapter 8, section 8.4; TD-1).
>
> **Open question:** Which secret store mechanism supplies provider credentials? Deployment configuration/secrets are required, but the concrete store is a later decision (Chapter 7, section 7.3; Chapter 8, section 8.6).

---

### Frontend sub-stories

Not applicable. The user interface is out of scope (Chapter 1, scope notes; Chapter 3, business scope), and the rate-provider integration is internal to the Wallet Function (Chapter 5, section 5.2). The investor only observes the resulting valuation through the HTTP API.

---

### Backend sub-stories

#### RATE-BE-001.1: Valuation depends only on the RateProvider port

**Parent:** RATE-STORY-001
**Architecture references:** Chapter 5, section 5.2 (RateProvider port, Valuation Domain Service); Chapter 8, section 8.4 (interface-first integration); ADR-002; QS-3

##### RATE-BE-001.1-S1: A rate is requested through the domain port

**GIVEN**
* The Valuation Domain Service is configured with a fake RateProvider that returns 100 for bitcoin to USD
* A wallet holds 2 stocks of type "bitcoin"

**WHEN**
* The domain service computes the wallet value in USD

**THEN**
* The fake RateProvider is asked for the bitcoin-to-USD rate
* The returned total is 200 USD using that rate

##### RATE-BE-001.1-S2: Domain tests need no provider technology

**GIVEN**
* The Valuation Domain Service is configured with an in-memory fake RateProvider
* No AWS services and no external HTTP provider are available

**WHEN**
* The valuation unit tests are run

**THEN**
* The domain code executes through the RateProvider port alone, with no provider-specific HTTP payload types
* The tests pass without network or cloud dependencies

#### RATE-BE-001.2: Exchange Rate Provider Adapter translates rate requests and responses

**Parent:** RATE-STORY-001
**Architecture references:** Chapter 5, section 5.2 (Exchange Rate Provider Adapter); Chapter 8, section 8.4 (adapter responsibilities, configuration); Chapter 3, section 3.2, I-2 (HTTPS/REST); R-2

##### RATE-BE-001.2-S1: Provider response is normalized into a domain rate

**GIVEN**
* The adapter is configured with a provider endpoint and its HTTP client is mocked
* The mocked provider returns a rate for the requested stock type/currency pair

**WHEN**
* The domain asks the adapter for the bitcoin-to-USD rate

**THEN**
* The adapter sends an HTTPS/REST request to the configured provider for that stock type/currency pair
* The provider response is interpreted and normalized into a domain-friendly exchange rate
* The normalized rate is returned to the domain through the RateProvider port

##### RATE-BE-001.2-S2: Provider-specific details stay at the adapter boundary

**GIVEN**
* The mocked provider response uses the provider's own field names and format

**WHEN**
* The adapter translates the response

**THEN**
* The rate delivered to the domain contains no provider-specific field names or payload structures
* The RateProvider port contract is unchanged by the provider's response format

#### RATE-BE-001.3: Invalid or failed provider data never becomes a rate

**Parent:** RATE-STORY-001
**Architecture references:** Chapter 8, section 8.3 (adapter validation/normalization) and section 8.4 (map errors/timeouts to explicit errors); Chapter 6, section 6.2 (steps 5-6); ADR-004; R-2
**Note:** The end-to-end HTTP error response and the no-partial-total guarantee are covered by VALUATION-STORY-002 (Supporting).

##### RATE-BE-001.3-S1: Malformed provider response is rejected

**GIVEN**
* The mocked provider returns a response with a missing or unparseable rate value

**WHEN**
* The adapter processes the response

**THEN**
* An explicit rate-provider error is raised
* No default, estimated or invented rate is substituted

##### RATE-BE-001.3-S2: Provider error signal is mapped explicitly

**GIVEN**
* The mocked provider returns an error response for the requested stock type/currency pair

**WHEN**
* The adapter processes the response

**THEN**
* An application/domain-relevant rate-provider error is raised
* No normalized exchange rate is returned to the domain

---

### Infrastructure sub-stories

#### RATE-INFRA-001.1: Deploy the function with external rate provider integration

**Parent:** RATE-STORY-001
**Architecture references:** Chapter 7, sections 7.2 and 7.3 (Configuration, Security boundaries); ADR-001; TC-4; TC-5; TC-6

##### RATE-INFRA-001.1-S1: Provider connectivity comes from deployment configuration

**GIVEN**
* The AWS SAM template defines the Wallet Function with rate provider endpoint and timeout settings as environment configuration

**WHEN**
* A developer runs `sam build` and `sam deploy`

**THEN**
* The function can call the configured rate provider over HTTPS/REST
* Outbound provider traffic uses HTTPS
* No provider credentials or API keys are embedded in the deployed function code

#### RATE-INFRA-001.2: Data store for the wallet being valued

**Parent:** RATE-STORY-001
**Architecture references:** Chapter 7, section 7.2 (Wallet Table); Chapter 8, section 8.5 (Persistence); TC-3; TD-2

##### RATE-INFRA-001.2-S1: Wallet data is read from the DynamoDB table

**GIVEN**
* The AWS SAM template provisions the Wallet Table with on-demand billing
* The AWS SDK is mocked in the adapter test

**WHEN**
* A valuation that needs an external rate loads a wallet through the DynamoDB Wallet Repository

**THEN**
* The repository reads the wallet aggregate from the Wallet Table through the DynamoDB API over HTTPS
* The wallet data used in the valuation comes from that table
* No provisioned database capacity needs to be managed

#### RATE-INFRA-001.3: Event handling

Not applicable. Rate lookup is a synchronous HTTPS/REST request/response integration (Chapter 4, section 4.2; Chapter 3, section 3.2, I-2; Chapter 6, section 6.1, runtime steps 7-9). No events, queues or dead-letter handling are part of this flow.

#### RATE-INFRA-001.4: Monitoring and observability of provider calls

**Parent:** RATE-STORY-001
**Architecture references:** Chapter 7, section 7.3 (Observability); Chapter 8, section 8.7 (Logging, Observability, and Diagnostics); R-1; R-4

##### RATE-INFRA-001.4-S1: Rate lookups are observable

**GIVEN**
* The stack is deployed

**WHEN**
* The adapter performs a rate lookup during a valuation

**THEN**
* The lookup context and outcome are logged to CloudWatch Logs as structured fields
* Lambda duration metrics are available to observe provider-call latency
* The logs exclude provider credentials and full provider payloads
