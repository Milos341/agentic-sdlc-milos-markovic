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

#### RATE-INFRA-001.1: The Dockerfile builds successfully

**Parent:** RATE-STORY-001
**Architecture references:** Chapter 7, sections 7.2 and 7.3; ADR-001; TC-4; TC-5; TC-6; `Dockerfile`; `.github/workflows/ci.yml`. The AWS serverless deployment (Chapter 7, ADR-001) remains the documented target architecture, but it is out of scope for the INFRA stories of this exercise.

##### RATE-INFRA-001.1-S1: Docker image builds

**GIVEN**
* The repository contains a `Dockerfile` based on `python:3.12-slim` and a valid `requirements.txt`

**WHEN**
* A developer runs `docker build -t kata-tests .`

**THEN**
* The command exits with code 0
* A Docker image tagged `kata-tests` is produced

#### RATE-INFRA-001.2: The test suite runs inside the Docker container

**Parent:** RATE-STORY-001
**Architecture references:** Chapter 7, section 7.3; ADR-001; TC-4; `Dockerfile`; `.github/workflows/ci.yml`. The AWS serverless deployment (Chapter 7, ADR-001) remains the documented target architecture, but it is out of scope for the INFRA stories of this exercise.

##### RATE-INFRA-001.2-S1: Pytest executes in the container

**GIVEN**
* The `kata-tests` Docker image has been built successfully

**WHEN**
* A developer runs `docker run --rm kata-tests`

**THEN**
* The command exits with code 0
* Pytest runs the tests under `tests/` and reports all tests passed

#### RATE-INFRA-001.3: Dependencies are installed correctly

**Parent:** RATE-STORY-001
**Architecture references:** Chapter 7, section 7.3; ADR-001; TC-4; `Dockerfile`; `requirements.txt`. The AWS serverless deployment (Chapter 7, ADR-001) remains the documented target architecture, but it is out of scope for the INFRA stories of this exercise.

##### RATE-INFRA-001.3-S1: Requirements are installed during image build

**GIVEN**
* `requirements.txt` declares the project test dependencies (including `pytest>=8.0`)

**WHEN**
* A developer runs `docker build -t kata-tests .`

**THEN**
* The build step `pip install --no-cache-dir -r requirements.txt` completes with exit code 0
* The resulting image contains the installed dependencies required to run `pytest`

#### RATE-INFRA-001.4: The project structure supports pytest discovery

**Parent:** RATE-STORY-001
**Architecture references:** Chapter 7, section 7.3; ADR-001; TC-4; `Dockerfile`; `tests/`. The AWS serverless deployment (Chapter 7, ADR-001) remains the documented target architecture, but it is out of scope for the INFRA stories of this exercise.

##### RATE-INFRA-001.4-S1: Pytest discovers tests from the tests directory

**GIVEN**
* The source code is copied to `/app/src` and the tests are copied to `/app/tests` in the Docker image
* The container default command is `pytest tests/ -v --tb=short`

**WHEN**
* A developer runs `docker run --rm kata-tests`

**THEN**
* Pytest collects tests from the `tests/` directory without import or discovery errors
* The command exits with code 0 when all discovered tests pass
