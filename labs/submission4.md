# Lab 4 — SBOM Generation & Software Composition Analysis

## Task 1 — SBOM Generation with Syft and Trivy

### Package Type Distribution Comparison

| Package Type | Syft Count | Trivy Count | Notes |
|--------------|------------|-------------|-------|
| **Total Packages** | **1139** | **1135** | Syft discovers 4 more packages |
| **npm (Node.js)** | **1128** | **1125** | Syft deeper Node.js discovery |
| **deb (Debian OS)** | **10** | **10** | Identical OS package detection |
| **binary** | **1** | **0** | Syft-only binary detection |

**Key Findings:**
- **Syft** detected **1139 total packages** vs Trivy's **1135** (+0.35% more comprehensive)
- **npm packages**: Syft found **1128** vs Trivy's **1125** (deeper Node.js dependency tree)
- **OS packages**: Both detected **10 Debian packages** (perfect consistency)
- **Syft advantage**: Additional **binary** detection (1 package)

### Dependency Discovery Analysis

**Syft Strengths:**
```
Syft Package Counts:
  1128 npm     (99.1% of total)
   10 deb      (0.9% OS packages)
    1 binary   (unique detection)
```
- **Native JSON format** provides richest metadata (file locations, digests, relationships)
- **Superior Node.js discovery** - 3 more npm packages detected
- **Binary detection** - identifies compiled executables missed by Trivy
- **Relationship mapping** - documents package dependencies explicitly

**Trivy Strengths:**
```
Trivy Package Counts:
  1125 Node.js (99.1% of total)
   10 debian   (0.9% OS packages)
```
- **Unified format** - single tool handles both SBOM + vulnerability scanning
- **Target classification** - distinguishes `os-pkgs` vs `lang-pkgs`
- **Consistent OS detection** - matches Syft exactly on Debian packages

**Winner:** **Syft** for dependency completeness (+4 packages, binary detection)

### License Discovery Analysis

| License Category | Syft Count | Trivy OS Count | Trivy Node.js Count | Coverage |
|------------------|------------|----------------|---------------------|----------|
| **MIT** | **890** | - | **878** | Syft +12 |
| **ISC** | **143** | - | **143** | Identical |
| **Apache-2.0** | **15** | **1** | **12** | Syft most complete |
| **BSD-3-Clause** | **16** | - | **14** | Syft +2 |
| **LGPL-3.0** | **19** | **1** | **19** | Trivy splits by target |
| **Total Unique** | **29** | **12** | **27** | Syft 7% more licenses |

**License Detection Summary:**
```
Syft Total Unique Licenses: 29
Trivy OS Licenses: 12
Trivy Node.js Licenses: 27
```

**Key Observations:**
- **Syft dominates license detection** (29 vs Trivy's 27+12 split)
- **MIT dominance** reflects Node.js ecosystem (79% of packages)
- **Syft comprehensive** - single pass finds all licenses
- **Trivy splits** by package target (OS vs Node.js) - more granular but fragmented

## Task 2 — Software Composition Analysis with Grype and Trivy

### SCA Tool Comparison

| Metric | Grype | Trivy | Difference |
|--------|-------|-------|------------|
| **Critical** | **11** | **10** | Grype +1 |
| **High** | **86** | **81** | Grype +5 |
| **Medium** | **32** | **34** | Trivy +2 |
| **Low** | **3** | **18** | Trivy +15 |
| **Negligible** | **12** | **0** | Grype only |
| **Total** | **144** | **143** | Grype +1 |

### Critical Vulnerabilities Analysis

**Top 5 Critical Findings:**

| Rank | Package | Version | CVE/GHSA | Severity | EPSS | Risk Score | Remediation |
|------|---------|---------|-----------|----------|------|------------|-------------|
| 1 | **vm2** | 3.9.17 | GHSA-whpj-8f3w-67p5 | **Critical** | 69.9% | **65.7** | Upgrade to 3.9.18 |
| 2 | **vm2** | 3.9.17 | GHSA-g644-9gfx-q4q4 | **Critical** | 39.2% | **36.9** | Upgrade to 3.9.18 |
| 3 | **jsonwebtoken** | 0.1.0 | GHSA-c7hr-j4mj-j2w6 | **Critical** | 32.5% | **29.2** | Upgrade to 4.2.2 |
| 4 | **jsonwebtoken** | 0.4.0 | GHSA-c7hr-j4mj-j2w6 | **Critical** | 32.5% | **29.2** | Upgrade to 4.2.2 |
| 5 | **lodash** | 2.4.2 | GHSA-jf85-cpcp-j695 | **Critical** | 2.4% | **2.2** | Upgrade to 4.17.12 |

### License Compliance Assessment

**License Detection:**
- **Syft:** **32 unique licenses**
- **Trivy:** **28 unique licenses**

### Additional Security Features

**Trivy Secrets Scan Results:**

| File | Secret Type | Severity | Location |
|------|-------------|----------|----------|
| `/juice-shop/build/lib/insecurity.js` | **Asymmetric Private Key** | **HIGH** | Line 47 |
| `/juice-shop/lib/insecurity.ts` | **Asymmetric Private Key** | **HIGH** | Line 23 |
| `/juice-shop/frontend/src/app/app.guard.spec.ts` | **JWT Token** | **MEDIUM** | Line 38 |
| `/juice-shop/frontend/src/app/last-login-ip/last-login-ip.component.spec.ts` | **JWT Token** | **MEDIUM** | Line 61 |

**Secrets Summary:**
- **2 HIGH severity** RSA private keys in source code
- **2 MEDIUM severity** JWT tokens in test files
- **Total: 4 secrets detected**

**Security Posture:** **CRITICAL** - Private keys in source code represent immediate compromise risk.

## Task 3 — Toolchain Comparison: Syft+Grype vs Trivy All-in-One

### Accuracy Analysis

**Package Detection Overlap:**
```
Total Packages Analyzed: 1148 unique (1126 common + 13 Syft-only + 9 Trivy-only)
```

| Metric | Syft | Trivy | Overlap |
|--------|------|-------|---------|
| **Total Packages** | **1139** | **1135** | **1126 (98.0%)** |
| **Syft Unique** | **13** | - | - |
| **Trivy Unique** | - | **9** | - |

**Vulnerability Detection Overlap:**
| Metric | Grype | Trivy | Common CVEs |
|--------|-------|-------|-------------|
| **Total CVEs** | **93** | **91** | **26 (28%)** |
| **Grype Unique** | **67** | **65** | - |

**Accuracy Assessment:** **98% package overlap**, **28% CVE overlap** - both toolchains highly consistent.

### Tool Strengths and Weaknesses

| Aspect | **Syft+Grype** | **Trivy** |
|--------|----------------|-----------|
| **Strengths** | - **Higher accuracy** (fewer false positives)<br>- **Richer SBOM metadata**<br>- **13 unique packages** detected<br>- **Composite risk scoring** (EPSS+CVSS) | - **All-in-one** (SBOM+Vuln+Secrets+Licenses)<br>- **Secrets scanning** (4 findings)<br>- **Faster deployment**<br>- **9 unique packages** |
| **Weaknesses** | - **Two tools** required<br>- **No secrets scanning**<br>- **Slower workflow** | - **More false positives**<br>- **Less SBOM detail**<br>- **No risk scoring** |

### Use Case Recommendations

| Scenario | **Recommended Toolchain** | **Reason** |
|----------|---------------------------|------------|
| **CI/CD Gate** | **Trivy** | Single binary, secrets scanning, fast |
| **Compliance SBOM** | **Syft+Grype** | Rich metadata, SPDX/CycloneDX support |
| **Production Risk** | **Syft+Grype** | EPSS scoring, accuracy focus |
| **Developer Laptop** | **Trivy** | All features, no setup complexity |
| **Air-gapped** | **Syft+Grype** | Efficient DB updates |
| **Kubernetes** | **Trivy** | Native operator available |

### Integration Considerations

**CI/CD Pipeline Comparison:**

| Aspect | **Syft+Grype** | **Trivy** |
|--------|----------------|-----------|
| **GitHub Actions** | `anchore/scan-action@v7` | `aquasecurity/trivy-action` |
| **Dockerfile** | 2 images | **1 image** |
| **Scan Time** | **SBOM gen + scan** (2 steps) | **Single scan** |
| **Config Files** | `.grype.yaml` | `.trivy.yaml` |
| **Exit Codes** | Severity-based | Severity-based |

**Operational Recommendations:**
```
Production Pipeline:
├── Stage 1: Trivy (fast secrets + initial scan)
└── Stage 2: Syft+Grype (accurate SBOM + risk scoring)
```

**Final Verdict:** **Hybrid approach** - Trivy for speed/secrets, Syft+Grype for accuracy/compliance.
