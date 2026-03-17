# Lab 2 — Threat Modeling with Threagile

## Task 1 — Threagile Baseline Model

### 1.1 Baseline Model Generation

**Command Used:**
```bash
docker run --rm -v "$(pwd)":/app/work threagile/threagile \
  -model /app/work/labs/lab2/threagile-model.yaml \
  -output /app/work/labs/lab2/baseline \
  -generate-risks-excel=false -generate-tags-excel=false
```

**Generated Outputs:**
- `report.pdf` — Full threat model report with diagrams
- `risks.json` — Structured risk data (23 total risks identified)
- `stats.json` — Risk statistics (4 elevated, 14 medium, 5 low)
- `technical-assets.json` — Asset inventory
- Data-flow and data-asset diagrams (PNG)

### 1.2 Risk Analysis Methodology

**Composite Score Calculation:**

The composite score prioritizes severity while factoring in likelihood and impact:

- **Severity weights:** critical (5), elevated (4), high (3), medium (2), low (1)
- **Likelihood weights:** very-likely (4), likely (3), possible (2), unlikely (1)
- **Impact weights:** high (3), medium (2), low (1)

**Formula:** `Composite Score = Severity × 100 + Likelihood × 10 + Impact`

**Example Calculation (Risk #1):**
- Severity: elevated = 4
- Likelihood: likely = 3
- Impact: high = 3
- **Score:** (4 × 100) + (3 × 10) + 3 = 400 + 30 + 3 = **433**

This weighting ensures severity dominates the ranking (100x multiplier), while likelihood and impact provide granular differentiation between risks of equal severity.

### 1.3 Top 5 Risks Identified

| Rank | Risk Title | Severity | Category | Asset | Likelihood | Impact | Score |
|------|-----------|----------|----------|-------|------------|--------|-------|
| 1 | Unencrypted Communication named Direct to App (no proxy) between User Browser and Juice Shop Application transferring authentication data | elevated | unencrypted-communication | user-browser | likely | high | 433 |
| 2 | Unencrypted Communication named To App between Reverse Proxy and Juice Shop Application | elevated | unencrypted-communication | reverse-proxy | likely | medium | 432 |
| 3 | Missing Authentication covering communication link To App from Reverse Proxy to Juice Shop Application | elevated | missing-authentication | juice-shop | likely | medium | 432 |
| 4 | Cross-Site Scripting (XSS) risk at Juice Shop Application | elevated | cross-site-scripting | juice-shop | likely | medium | 432 |
| 5 | Cross-Site Request Forgery (CSRF) risk at Juice Shop Application via Direct to App (no proxy) from User Browser | medium | cross-site-request-forgery | juice-shop | very-likely | low | 241 |

### 1.4 Critical Security Concerns Analysis

**1. Unencrypted Communication (Ranks #1-2):**
The absence of TLS/HTTPS encryption between the user browser and application exposes authentication credentials, session tokens, and sensitive customer data to network-level eavesdropping and man-in-the-middle attacks. This is the most severe architectural flaw, affecting both direct browser-to-app and reverse-proxy-to-app communication paths.

**2. Missing Authentication (Rank #3):**
The communication link between the reverse proxy and Juice Shop application lacks authentication mechanisms, allowing any process or attacker with network access to interact with the application backend, bypassing intended access controls and enabling unauthorized API calls.

**3. Client-Side Injection Attacks (Ranks #4-5):**
The application is vulnerable to Cross-Site Scripting (XSS) and Cross-Site Request Forgery (CSRF) attacks. XSS allows attackers to inject malicious scripts that execute in users' browsers, potentially stealing credentials or manipulating the DOM. CSRF enables unauthorized actions by exploiting authenticated user sessions through forged requests.

**4. Overall Risk Posture:**
With 4 elevated-severity risks and 14 medium-severity risks, the baseline deployment demonstrates a high-risk security posture typical of intentionally vulnerable applications. The concentration of risks around unencrypted communications and missing security controls indicates systemic architectural weaknesses rather than isolated vulnerabilities.

### 1.5 Generated Diagrams

**Data Flow Diagram:**

![Baseline Data Flow Diagram](./lab2/baseline/data-flow-diagram.png)

**Data Asset Diagram:**

![Baseline Data Asset Diagram](./lab2/baseline/data-asset-diagram.png)

The diagrams illustrate the trust boundaries, communication flows, and data asset processing pathways identified in the threat model. Red indicators highlight unencrypted communication links and missing security controls.

## Task 2 — HTTPS Variant & Risk Comparison

### 2.1 Secure Model Variant Creation

**Changes Applied to Model:**

1. **User Browser → Juice Shop Application:** Changed `protocol: http` → `protocol: https`

2. **Reverse Proxy → Juice Shop Application:** Changed `protocol: http` → `protocol: https`

3. **Persistent Storage (Database):** Changed `encryption: none` → `encryption: transparent`

**File Location:** `labs/lab2/threagile-model.secure.yaml`

### 2.2 Secure Variant Generation Results

**Command Used:**
```bash
docker run --rm -v "$(pwd)":/app/work threagile/threagile \
  -model /app/work/labs/lab2/threagile-model.secure.yaml \
  -output /app/work/labs/lab2/secure \
  -generate-risks-excel=false -generate-tags-excel=false
```

**Generated Outputs:**
- `report.pdf` — Updated threat model with security controls applied
- `risks.json` — Risk data reflecting HTTPS and encryption improvements
- `stats.json` — Updated risk statistics (20 total risks)
- Diagrams showing secure architecture with protected communication channels

### 2.3 Risk Category Delta Analysis

| Category | Baseline | Secure | Δ |
|---|---:|---:|---:|
| container-baseimage-backdooring | 1 | 1 | 0 |
| cross-site-request-forgery | 2 | 2 | 0 |
| cross-site-scripting | 1 | 1 | 0 |
| missing-authentication | 1 | 1 | 0 |
| missing-authentication-second-factor | 2 | 2 | 0 |
| missing-build-infrastructure | 1 | 1 | 0 |
| missing-hardening | 2 | 2 | 0 |
| missing-identity-store | 1 | 1 | 0 |
| missing-vault | 1 | 1 | 0 |
| missing-waf | 1 | 1 | 0 |
| server-side-request-forgery | 2 | 2 | 0 |
| unencrypted-asset | 2 | 1 | -1 |
| unencrypted-communication | 2 | 0 | -2 |
| unnecessary-data-transfer | 2 | 2 | 0 |
| unnecessary-technical-asset | 2 | 2 | 0 |

**Total Risk Count:**
- Baseline: 23 risks
- Secure: 20 risks
- **Reduction: -3 risks (13.0% decrease)**

### 2.4 Top 5 Risks in Secure Variant

| Rank | Risk Title | Severity | Category | Asset | Likelihood | Impact | Score |
|------|-----------|----------|----------|-------|------------|--------|-------|
| 1 | Cross-Site Scripting (XSS) risk at Juice Shop Application | elevated | cross-site-scripting | juice-shop | likely | medium | 432 |
| 2 | Missing Authentication covering communication link To App from Reverse Proxy to Juice Shop Application | elevated | missing-authentication | juice-shop | likely | medium | 432 |
| 3 | Cross-Site Request Forgery (CSRF) risk at Juice Shop Application via Direct to App (no proxy) from User Browser | medium | cross-site-request-forgery | juice-shop | very-likely | low | 241 |
| 4 | Cross-Site Request Forgery (CSRF) risk at Juice Shop Application via To App from Reverse Proxy | medium | cross-site-request-forgery | juice-shop | very-likely | low | 241 |
| 5 | Missing Hardening risk at Juice Shop Application | medium | missing-hardening | juice-shop | likely | low | 231 |

**Notable Change:** Unencrypted communication risks that dominated the baseline top 5 (ranks #1-2, scores 433-432) have been completely eliminated. The secure variant's top risks now focus on application-layer vulnerabilities (XSS, CSRF) and architectural gaps (missing authentication, hardening).

### 2.5 Delta Run Explanation

#### Specific Changes and Their Impact

**1. HTTPS Protocol Implementation (Δ = -2 unencrypted-communication risks)**

By upgrading communication protocols from HTTP to HTTPS for both user-to-app and proxy-to-app links, Threagile eliminated **all 2 unencrypted-communication risks**. HTTPS provides:
- **Transport Layer Security (TLS):** Encrypts all data in transit using strong cryptographic algorithms, preventing passive eavesdropping
- **Certificate-based Authentication:** Validates server identity through PKI, preventing man-in-the-middle attacks
- **Integrity Protection:** Uses HMAC to detect any tampering with transmitted data

**Why this reduced risks:** Network-level attackers can no longer intercept authentication credentials, session tokens, or customer data during transmission. The threat model recognized that encrypted channels eliminate passive network sniffing and active MITM attack vectors that were present in the baseline HTTP deployment.

**2. Database Encryption at Rest (Δ = -1 unencrypted-asset risk)**

Enabling transparent encryption for the Persistent Storage (SQLite database) reduced unencrypted-asset risks from 2 to 1 (50% reduction). This change:
- Protects data files from unauthorized file system access
- Mitigates risks from container escape or host compromise scenarios
- Ensures confidentiality even if storage media is physically accessed

**Why this reduced risks:** Threagile recognized that the customer-data and authentication-token data assets are no longer stored in plaintext. Physical or logical access to database files no longer directly exposes confidential information. The remaining unencrypted-asset risk likely pertains to in-memory data processing or temporary files.

#### Observed Results Summary

The secure variant achieved a **13.0% risk reduction** (23 → 20 risks) by implementing encryption controls:

**Eliminated Risk Categories:**
- Unencrypted communication: 100% eliminated (2 → 0)
- Unencrypted assets: 50% reduction (2 → 1)

#### Why These Changes Work

- **Encryption in transit (HTTPS):** Protects against network-layer attackers
- **Encryption at rest (transparent database encryption):** Protects against storage-layer attackers
- **Remaining gaps:** Require application and architectural controls for comprehensive security

### 2.6 Diagram Comparison

**Baseline Architecture:**
![Baseline Data Flow Diagram](./lab2/baseline/data-flow-diagram.png)

**Secure Architecture:**
![Secure Data Flow Diagram](./lab2/secure/data-flow-diagram.png)

**Key Visual Differences:**
- Communication links now display HTTPS protocol indicators
