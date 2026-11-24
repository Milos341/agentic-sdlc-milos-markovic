# WALLET Domain: Story Bundles

## WALLET-STORY-001: Add a stock to the wallet

**AS A** investor
**I WANT** to add a stock (stock type and quantity) to my wallet
**SO THAT** my holdings are recorded and can be valued later

**Priority:** Core (Pareto 20%)

**Architecture references:**
- Chapter 1, FR-1 (Manage wallet stocks)
- Chapter 5, section 5.2 (Wallet API Handler, Wallet Application Service, DynamoDB Wallet Repository)
- Chapter 8, section 8.3 (Validation) and section 8.5 (Persistence)

### WALLET-STORY-001-S1: Successful add

**GIVEN**
* I have a wallet
* The wallet does not contain any bitcoin

**WHEN**
* I add a stock of type "bitcoin" with quantity 2

**THEN**
* The wallet contains a stock of type "bitcoin" with quantity 2
* The response confirms the stored stock

### WALLET-STORY-001-S2: Invalid quantity is rejected

**GIVEN**
* I have a wallet

**WHEN**
* I add a stock with quantity -5

**THEN**
* The request is rejected with a clear validation error (HTTP 4xx)
* The wallet is unchanged

### WALLET-STORY-001-S3: Missing stock type is rejected

**GIVEN**
* I have a wallet

**WHEN**
* I add a stock without a stock type

**THEN**
* The request is rejected with a clear validation error (HTTP 4xx)
* The wallet is unchanged

> **Open question:** What happens when a stock of an already present type is added (replace or increase the quantity)? The architecture does not decide this. It is a later decision (see TD-3, API contract).

---

### Frontend sub-stories

Not applicable. The user interface is out of scope (Chapter 1, scope notes; Chapter 3, business scope). The system is an HTTP API.

---

### Backend sub-stories

#### WALLET-BE-001.1: HTTP endpoint to add a stock

**Parent:** WALLET-STORY-001
**Architecture references:** Chapter 5 (Wallet API Handler), Chapter 8.3 (API boundary validation), QS-7
**Note:** Route and request schema are defined in the API contract (TD-3).

##### WALLET-BE-001.1-S1: Valid request

**GIVEN**
* The Wallet API Handler receives a request with stock type "bitcoin" and quantity 2

**WHEN**
* The handler processes the request

**THEN**
* The use case "add stock" is called with the parsed values
* The handler returns a success response containing the stored stock

##### WALLET-BE-001.1-S2: Invalid request

**GIVEN**
* The Wallet API Handler receives a request with quantity -5

**WHEN**
* The handler processes the request

**THEN**
* The handler returns a 4xx error with a descriptive message
* The use case is not called
* The error response contains no stack trace or internal details

#### WALLET-BE-001.2: Add-stock use case and domain rules

**Parent:** WALLET-STORY-001
**Architecture references:** Chapter 5 (Wallet Application Service), Chapter 8.1 (Quantity), Chapter 8.3 (domain invariants), ADR-002

##### WALLET-BE-001.2-S1: Stock is added to the wallet

**GIVEN**
* A fake WalletRepository holds an empty wallet

**WHEN**
* The use case adds a stock "bitcoin" with quantity 2

**THEN**
* The wallet saved through the repository contains the stock "bitcoin" with quantity 2

##### WALLET-BE-001.2-S2: Domain rejects an invalid quantity

**GIVEN**
* A fake WalletRepository holds an empty wallet

**WHEN**
* The use case adds a stock with quantity -5

**THEN**
* An invalid-quantity error is raised
* Nothing is saved through the repository

#### WALLET-BE-001.3: DynamoDB wallet persistence

**Parent:** WALLET-STORY-001
**Architecture references:** Chapter 5 (DynamoDB Wallet Repository), Chapter 8.5, ADR-001, ADR-002, TD-2

##### WALLET-BE-001.3-S1: Saved wallet can be loaded again

**GIVEN**
* A wallet with the stock "bitcoin" and quantity 2 is saved through the DynamoDB Wallet Repository (AWS SDK mocked)

**WHEN**
* The wallet is loaded by its identifier

**THEN**
* The loaded wallet contains the stock "bitcoin" with quantity 2

---

### Infrastructure sub-stories

#### WALLET-INFRA-001.1: Deploy the API and the Wallet Function

**Parent:** WALLET-STORY-001
**Architecture references:** Chapter 7, sections 7.2 and 7.3; ADR-001; TC-4

##### WALLET-INFRA-001.1-S1: Deployment with SAM

**GIVEN**
* The AWS SAM template defines the HTTP API and the Wallet Function

**WHEN**
* A developer runs `sam build` and `sam deploy`

**THEN**
* The API endpoint is reachable over HTTPS
* The Wallet Function runs on Python 3.12
* The function's execution role can access the Wallet Table only

#### WALLET-INFRA-001.2: Create the Wallet Table

**Parent:** WALLET-STORY-001
**Architecture references:** Chapter 7 (Wallet Table), ADR-001, TC-3, TD-2

##### WALLET-INFRA-001.2-S1: Table is provisioned on demand

**GIVEN**
* The AWS SAM template defines the Wallet Table with on-demand billing

**WHEN**
* The stack is deployed

**THEN**
* The Wallet Table exists with on-demand capacity
* No provisioned capacity needs to be managed

#### WALLET-INFRA-001.3: Event handling

Not applicable. The system uses synchronous request and response and no events (Chapter 4, section 4.2).

#### WALLET-INFRA-001.4: Monitoring and observability

**Parent:** WALLET-STORY-001
**Architecture references:** Chapter 7, section 7.3; Chapter 8, section 8.7

##### WALLET-INFRA-001.4-S1: Logs and metrics are available

**GIVEN**
* The stack is deployed

**WHEN**
* A request to add a stock is processed

**THEN**
* The Lambda invocation is logged to CloudWatch Logs
* API Gateway and Lambda metrics (requests, errors, duration) are available
