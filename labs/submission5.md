# Lab 5 — Security Analysis: SAST & DAST of OWASP Juice Shop

## Task 1 — Static Application Security Testing with Semgrep

### SAST Tool Effectiveness

**Semgrep Coverage & Results:**
- **Files Scanned:** **1014 files** tracked by git
- **Rules Applied:** **674 Community rules** across 8 languages
- **Findings:** **25 Blocking vulnerabilities**
- **Parsed Lines:** **~99.9%** coverage
- **Skipped:** 139 files (`.semgrepignore`), 8 files >1MB

**Vulnerability Types Detected:**
1. **SQL Injection** (9 findings) - Sequelize injection via user-controlled `criteria`
2. **Path Traversal** (5 findings) - `res.sendFile()` with user input
3. **Hardcoded Secret** (1 finding) - JWT private key in `insecurity.ts`
4. **XSS** (4 findings) - Unquoted HTML attributes + script tag injection
5. **Open Redirect** (2 findings) - `res.redirect()` with user input
6. **Code Injection** (1 finding) - `eval()` with user input
7. **Directory Listing** (1 finding) - Enabled on sensitive directories

**Coverage Assessment:** **Excellent** - scanned 1014/1153 files (88%), 25 actionable findings.

### Critical Vulnerability Analysis

**Top 5 Most Critical Findings:**

| # | **Vulnerability Type** | **File & Line** | **Severity** | **Details** |
|---|------------------------|-----------------|--------------|-------------|
| 1 | **SQL Injection** | `/src/data/static/codefixes/dbSchemaChallenge_1.ts:5` | **Blocking** | `models.sequelize.query("SELECT * FROM Products WHERE ((name LIKE '%"+criteria+"%'...`)` - User-controlled `criteria` directly interpolated |
| 2 | **Hardcoded Secret** | `/src/lib/insecurity.ts:56` | **Blocking** | `jwt.sign(user, privateKey, ...)` - Hardcoded JWT private key in source code |
| 3 | **Path Traversal** | `/src/routes/fileServer.ts:33` | **Blocking** | `res.sendFile(path.resolve('ftp/', file))` - Arbitrary file read via user-controlled `file` |
| 4 | **Code Injection** | `/src/routes/userProfile.ts:62` | **Blocking** | `username = eval(code)` - Arbitrary code execution via user input |
| 5 | **SQL Injection** | `/src/routes/login.ts:34` | **Blocking** | `models.sequelize.query("SELECT * FROM Users WHERE email = '${req.body.email...`)` - Login credentials directly interpolated |

**Semgrep Effectiveness:** Outstanding for Juice Shop - detected all intentional challenge vulns as **Blocking** severity.

## Task 2 — DAST Tool Comparison

### 1. Authenticated vs Unauthenticated Scanning

**ZAP Scan Comparison Results:**

| Metric | Unauthenticated | Authenticated | Δ |
|--------|-----------------|---------------|---|
| **Total Alerts** | **11** | **13** | +2 |
| **High** | **0** | **1** | +1 |
| **Medium** | **2** | **4** | +2 |
| **Low** | **6** | **4** | -2 |
| **Info** | **3** | **4** | +1 |
| **Unique URLs** | **15** | **23** | **+8** |

**Authenticated Endpoints Discovered:**
- `/rest/admin/application-configuration` (Private IP leak: `192.168.99.100:3000`)
- `/rest/user/login` (SQL Injection on `email` parameter)
- `/socket.io/` endpoints (Clickjacking, X-Frame-Options missing)

**Why Authenticated Matters:**
Authenticated scans access **protected endpoints** (admin panels, user data) missed by unauth scans. Juice Shop revealed **+8 URLs**, **1 HIGH SQLi**, and internal config leaks only after login.

### 2. Tool Comparison Matrix

| Tool | Findings | Severity Breakdown | Best Use Case |
|------|----------|--------------------|---------------|
| **ZAP** | **13** | 1 High, 4 Med, 4 Low, 4 Info | **Comprehensive web app scanning** with auth support |
| **Nuclei** | **3** | 0 High/Med, **3 Info** | **Fast template-based CVE/misconfig detection** |
| **Nikto** | **82** | 0 High, **~20 Med**, 62 Low/Info | **Server misconfig & backup file discovery** |
| **SQLmap** | **1** | **1 SQLi (Boolean-blind)** | **Deep SQL injection exploitation** |

### 3. Tool-Specific Strengths

**ZAP:**
- **Excels:** Full app crawling, auth handling, risk-based prioritization
- **Example:** `HIGH SQL Injection` on `/rest/products/search?q='(` - 500 error on payload

**Nuclei:**
- **Excels:** Speed (1000s templates), known exposures
- **Example:** `Public Swagger API` at `/api-docs/swagger.json` - API documentation leak

**Nikto:**
- **Excels:** Server headers, backup files, robots.txt
- **Example:** `/ftp/` in `robots.txt` returns 200 (not forbidden), **62 backup file probes** (`site.jks`, `dump.tar`)

**SQLmap:**
- **Excels:** Automated SQLi detection + exploitation
- **Example:** **Boolean-blind SQLi** on `/rest/products/search?q=` URI parameter (SQLite backend confirmed)

**Complementary Coverage:** ZAP (app logic), Nuclei (CVE), Nikto (misconfig), SQLmap (database).

## Task 3 — SAST/DAST Correlation and Security Assessment

### SAST vs DAST Comparison

**Total Findings Summary:**

| Tool Category | Findings Count | Scope |
|---------------|----------------|-------|
| **SAST (Semgrep)** | **25** | Code-level vulns |
| **DAST ZAP (Auth)** | **13** | Runtime app issues |
| **DAST Nuclei** | **3** | Template exposures |
| **DAST Nikto** | **82** | Server misconfigs |
| **DAST SQLmap** | **1** | SQL injection |
| **Total DAST** | **99** | Runtime + config |

**SAST: 25 findings** vs **DAST: 99 findings** (4x more runtime issues).

### Vulnerability Types Found ONLY by SAST

1. **Hardcoded JWT Secret** (`/src/lib/insecurity.ts:56`)
   - `jwt.sign(user, privateKey, ...)` - Static secret exposure
   - **SAST only:** Requires source code access

2. **Code Injection via `eval()`** (`/src/routes/userProfile.ts:62`)
   - `username = eval(code)` - Arbitrary code execution
   - **SAST only:** Detects dangerous API usage patterns

3. **Directory Listing Enabled** (`/src/server.ts:269`)
   - `serveIndex('ftp', { icons: true })` - Sensitive dir exposure
   - **SAST only:** Code configuration analysis

### Vulnerability Types Found ONLY by DAST

1. **Missing Security Headers** (ZAP/Nikto)
   - No X-XSS-Protection, X-Frame-Options, CSP missing
   - **DAST only:** Runtime HTTP response analysis

2. **Backup File Exposure** (Nikto - 62 findings)
   - `/site.jks`, `/dump.tar`, `/localhost.tgz` return 200
   - **DAST only:** Tests actual file existence

3. **Swagger API Documentation** (Nuclei)
   - `/api-docs/swagger.json` publicly accessible
   - **DAST only:** Discovers exposed endpoints

### Why Each Approach Finds Different Things

| Aspect | **SAST (Semgrep)** | **DAST (4 Tools)** |
|--------|--------------------|--------------------|
| **Analysis** | **Static code** review | **Runtime behavior** testing |
| **Strength** | Source code patterns | HTTP responses + config |
| **SAST Only** | Hardcoded secrets, `eval()`, code smells | Headers, file existence |
| **DAST Only** | Can't see runtime headers | Server misconfigs |
| **False Positives** | Code intent analysis | Network conditions |
| **Phase** | **Development/CI** | **Staging/Production** |

**Key Differences:**
1. **SAST** reads **source code** → finds hardcoded secrets, unsafe APIs (`eval()`)
2. **DAST** tests **running app** → finds missing headers, exposed files, live SQLi
3. **SAST** catches **developer mistakes** early
4. **DAST** validates **deployment/runtime** security

**Recommendation:** **Use both** - SAST prevents code issues, DAST validates deployment security.
