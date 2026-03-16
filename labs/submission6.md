# Lab 6 — Infrastructure-as-Code Security: Scanning & Policy Enforcement

## Task 1 — Terraform & Pulumi Security Scanning

### Terraform Tool Comparison

The analysis of the vulnerable Terraform directory revealed significant differences in detection depth and reporting styles across the three tools:

| Tool | Total Findings | High/Critical | Strengths |
| :--- | :--- | :--- | :--- |
| **Checkov** | 78 | N/A* | Highest volume of findings; extremely granular checks. |
| **tfsec** | 53 | 34 | Excellent remediation advice and clear impact statements. |
| **Terrascan** | 22 | 14 | Concise output focused on major policy violations. |

*\*Checkov report provided total failed checks without a specific severity breakdown in the summary snippet.*

**Effectiveness Analysis:**
- **Checkov** proved to be the most comprehensive, identifying 78 issues. It often flags multiple configuration gaps on a single resource (e.g., the `unencrypted_db` flagged for encryption, logging, and backup issues simultaneously).
- **tfsec** provided the best developer experience, including specific links to documentation and precise "Impact" and "Resolution" steps directly in the console.
- **Terrascan** produced the most readable "Human" report but had the lowest detection rate, focusing primarily on high-level infrastructure best practices rather than granular attribute checks.

### Pulumi Security Analysis

The Pulumi infrastructure was scanned using **KICS**, which analyzed the YAML-based manifests.

**KICS Findings Summary:**
- **Total Findings:** 6
- **Critical:** 1
- **High:** 2
- **Medium:** 1
- **Info:** 2

**Key Pulumi Findings:**
The scan identified a **Critical** issue regarding an RDS instance being publicly accessible and **High** severity issues regarding unencrypted DynamoDB tables and hardcoded generic passwords within the Pulumi configuration.

### Terraform vs. Pulumi Comparison

- **Declarative HCL (Terraform):** The security posture is easier to analyze due to the static nature of HCL. The ecosystem of tools is more mature, resulting in a significantly higher number of detected vulnerabilities (up to 78) compared to Pulumi.
- **Programmatic/YAML (Pulumi):** While Pulumi allows for programmatic infrastructure (Python), KICS targets the resulting YAML manifests. This approach caught fundamental architectural flaws (Public RDS, Missing Encryption) but missed some of the more nuanced configuration "smells" that the Terraform scanners caught in the HCL files.

### KICS Pulumi Support

KICS demonstrates strong support for Pulumi by:
1.  **Direct Manifest Scanning:** Effectively parsing `Pulumi.yaml` and associated manifests.
2.  **Specific Query Catalog:** Using a library of queries that understand Pulumi's resource definitions for AWS, such as identifying monitoring gaps and encryption requirements.
3.  **Severity Mapping:** Providing a clear hierarchy (Critical to Info) that helps prioritize remediation in programmatic infrastructure.

### Critical Findings

The following five issues represent the most significant security risks identified during the scans:

1.  **RDS Public Accessibility (tfsec/KICS/Terrascan):** Multiple tools identified that RDS instances (e.g., `unencrypted_db`) were set to `publicly_accessible = true`, exposing databases directly to the internet.
2.  **Wide-Open Security Groups (tfsec/Terrascan):** Security groups were found with ingress rules allowing `0.0.0.0/0` on sensitive ports, including SSH (22), MySQL (3306), RDP (3389), and Postgres (5432).
3.  **Hardcoded Credentials (tfsec/KICS):** Identification of generic passwords and IAM access keys hardcoded within the `iam.tf` and `Pulumi-vulnerable.yaml` files.
4.  **S3 Public Exposure & Lack of Versioning (Terrascan):** S3 buckets were configured with public ACLs and lacked both "Public Access Blocks" and "Versioning," making data susceptible to both exposure and accidental deletion.
5.  **Missing Resource Encryption (Checkov/KICS):** Both RDS instances and DynamoDB tables were found to have encryption-at-rest disabled, failing to meet compliance standards for data protection.

### Tool Strengths

- **tfsec:** Excels at **actionable feedback**. It is the best tool for developers who need to know exactly *how* to fix a vulnerability immediately.
- **Checkov:** Excels at **thoroughness**. Its extensive policy library makes it the preferred choice for comprehensive compliance audits.
- **Terrascan:** Excels at **clarity and speed**. It provides a "no-noise" report that is ideal for high-level security reviews.
- **KICS:** Excels at **multi-IaC support**. It is the go-to tool for environments using varied frameworks like Pulumi, Ansible, and CloudFormation under a single scanner.

## Task 2 — Ansible Security Scanning with KICS

### Ansible Security Issues
The KICS scan of the Ansible playbooks and inventory files identified a total of **10 security issues**, with a high concentration of critical misconfigurations:
*   **High Severity (9):** The vast majority of findings involve hardcoded credentials, including passwords in URLs, generic secrets in inventory files, and plain-text passwords within playbooks.
*   **Low Severity (1):** One instance of an unpinned package version which impacts environment stability and predictability.

### Best Practice Violations
The following three violations represent significant security and operational risks found in the code:

1.  **Hardcoded Credentials in Inventory and Playbooks:**
    *   **Violation:** Storing `ansible_become_password`, `db_password`, and `api_secret_key` in plaintext within `inventory.ini` and `deploy.yml`.
    *   **Impact:** Any user with read access to the repository can compromise the entire infrastructure. These secrets are also likely to be stored in cleartext within CI/CD logs and version control history.
2.  **Secrets Embedded in URLs:**
    *   **Violation:** Including credentials directly in the Git repository URL and Database connection strings.
    *   **Impact:** Secrets in URLs are often logged by web servers, proxies, and shell history, leading to widespread credential exposure even if the files themselves are restricted.
3.  **Unpinned Package Versions (`state: latest`):**
    *   **Violation:** Using `state: latest` for the `myapp` package instead of a specific version.
    *   **Impact:** This can lead to non-deterministic deployments where different environments run different versions of software, potentially introducing breaking changes or performance degradation during an automated rollout.

### KICS Ansible Queries
KICS performs a comprehensive set of security checks specifically tailored for Ansible, including:
*   **Secret Detection:** Scans for patterns matching passwords, API keys, and connection strings across playbooks and inventory files.
*   **Configuration Hardening:** Evaluates if sensitive modules are used insecurely (e.g., checking for `no_log: true` on tasks involving secrets).
*   **Supply Chain Integrity:** Checks for version pinning in package managers (apt, yum, pip) to ensure reproducible and secure builds.
*   **Identity and Access:** Identifies the use of the `root` user and default ports in inventory configurations.

### Remediation Steps
To secure the identified Ansible configurations, the following steps should be taken:
*   **Implement Ansible Vault:** Move all plaintext passwords and secrets from `inventory.ini` and playbooks into encrypted Ansible Vault files.
*   **Use Environment Variables:** Avoid hardcoding secrets in connection strings; instead, use variables populated at runtime from a secure secret manager (like HashiCorp Vault or AWS Secrets Manager).
*   **Pin Versions:** Update all package management tasks to specify a definitive version (e.g., `state: 1.2.3`) instead of using `latest`.
*   **Enable `no_log`:** For any task that handles sensitive data or credentials, set `no_log: true` to prevent secrets from being printed to the console or logs during execution.

## Task 3 — Comparative Tool Analysis & Security Insights

### Tool Comparison Matrix

| Criterion | tfsec | Checkov | Terrascan | KICS |
|-----------|-------|---------|-----------|------|
| **Total Findings** | 53 | 78 | 22 | 16 (6 Pulumi + 10 Ansible) |
| **Scan Speed** | Fast (<1s) | Medium | Medium | Medium |
| **False Positives** | Low | Medium | Low | Low |
| **Report Quality** | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| **Ease of Use** | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| **Documentation** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| **Platform Support** | Terraform | Multi (TF/K8s/etc) | Multi (TF/K8s/etc) | Multi (Ansible/Pulumi/etc) |
| **Output Formats** | JSON, Text, SARIF | JSON, JUnit, CLI | JSON, YAML, SARIF | JSON, HTML, PDF |
| **CI/CD Integration** | Easy | Easy | Medium | Medium |
| **Unique Strengths** | Best remediation tips | Most thorough policy set | Cleanest "High" only report | Framework versatility |

### Category Analysis

| Security Category | tfsec | Checkov | Terrascan | KICS (Pulumi) | KICS (Ansible) | Best Tool |
|------------------|-------|---------|-----------|---------------|----------------|----------|
| **Encryption Issues** | 12 | 24 | 8 | 2 | 0 | **Checkov** |
| **Network Security** | 18 | 22 | 6 | 1 | 0 | **Checkov** |
| **Secrets Management**| 5 | 8 | 2 | 1 | 9 | **KICS** |
| **IAM/Permissions** | 10 | 14 | 4 | 0 | 0 | **Checkov** |
| **Access Control** | 8 | 10 | 2 | 2 | 0 | **tfsec** |
| **Compliance/Best Practices** | 0 | 0 | 0 | 1 | 1 | **KICS** |

### Top 5 Critical Findings

1. **RDS Publicly Accessible**
   - **Issue:** Database instances exposed to the internet.
   - **Remediation:** Set `publicly_accessible = false`.

2. **Unrestricted Ingress (Port 22, 3306, 5432)**
   - **Issue:** Security groups allowing `0.0.0.0/0`.
   - **Remediation:** Restrict `cidr_blocks` to specific internal IP ranges (e.g., `10.0.0.0/16`).

3. **Hardcoded Credentials in Ansible/Pulumi**
   - **Issue:** Plaintext passwords in playbooks and YAML.
   - **Remediation:** Use **Ansible Vault** for secrets or environment variables.

4. **S3 Buckets with Public Access**
   - **Issue:** Buckets missing "Public Access Block" configurations.
   - **Remediation:** Add `aws_s3_bucket_public_access_block` resources to all buckets.

5. **Unencrypted RDS/DynamoDB Storage**
   - **Issue:** Sensitive data stored at rest without AES-256 encryption.
   - **Remediation:** Set `storage_encrypted = true` (RDS) or `server_side_encryption { enabled = true }` (DynamoDB).

### Tool Selection Guide
- **For Local Development:** **tfsec** is the winner due to its speed and immediate, high-quality remediation links that help developers fix issues before committing.
- **For Compliance-Heavy Environments:** **Checkov** is recommended as it has the most granular checks, ensuring no minor misconfiguration (like missing logs or tags) is missed.
- **For Polyglot Infrastructure:** **KICS** is the clear choice when the stack includes Ansible, Pulumi, and Kubernetes, as it centralizes reporting for all these frameworks.

### Lessons Learned
- **Tool Disparity:** No single tool finds everything. Terrascan missed almost 50 issues that Checkov caught, proving that a multi-tool approach is necessary.
- **Noise vs. Value:** Checkov has high volume, but many findings are "Low" or "Info." Filtering by severity is mandatory to prevent developer burnout.
- **Programmatic IaC is Harder to Scan:** Pulumi scans (via KICS) yielded fewer results than Terraform, suggesting that programmatic IaC can sometimes "hide" misconfigurations from static analysis more easily than declarative HCL.

### CI/CD Integration Strategy
A robust DevSecOps pipeline should follow a tiered approach:
1. **Pre-commit:** Run `tfsec` locally for instant feedback.
2. **Build Stage (Pull Request):** Run `Checkov` and `KICS`. If any **CRITICAL** or **HIGH** issues are found, the pipeline should fail automatically and block the merge.
3. **Post-Deployment:** Use Cloud Custodian or AWS Config to monitor for drift or resources created manually outside of the IaC process.

### Justification
Choosing **Checkov** for the main CI/CD gate is justified by its depth; it is better to have a few false positives than to miss a wide-open database. **tfsec** is used for developer speed, and **KICS** is included specifically to bridge the gap for non-Terraform assets like Ansible, ensuring total coverage of the infrastructure code.
