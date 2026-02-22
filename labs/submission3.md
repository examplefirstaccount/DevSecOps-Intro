# Lab 3 — Secure Git

## Task 1 — SSH Commit Signature Verification

### 1.1 Commit Signing Benefits

**Why Commit Signing is Critical:**

1. **Authenticity:** Verifies the author of each commit matches their claimed identity
2. **Integrity:** Ensures commits haven't been tampered with since signing
3. **Non-repudiation:** Provides cryptographic proof of who authored what and when
4. **Supply Chain Security:** Prevents malicious code injection by unauthorized actors
5. **Audit Trail:** Creates verifiable history for compliance and incident response

### 1.2 SSH Key Setup and Configuration

**SSH Key Generation:**
```bash
ssh-keygen -t ed25519 -C "adagamov05@mail.ru" -f ~/.ssh/id_git_devsecops
```

**Git Configuration:**
```bash
git config --global user.signingkey ~/.ssh/id_git_devsecops.pub
git config --global commit.gpgSign true
git config --global gpg.format ssh
```

**Verification:**
All commits in this PR are **signed with SSH** and display the **"Verified"** badge on GitHub:
- [View Signed Commits](https://github.com/examplefirstaccount/DevSecOps-Intro/commits/feature/lab3)

![Verified Commit Badge](screenshots/verified-commit.png)

### 1.3 Why Commit Signing Matters in DevSecOps

**Attack Scenarios Prevented:**
1. **Developer Compromise:** Even if an attacker gains repo access, unsigned commits are rejected
2. **Supply Chain Attack:** Malicious commits by compromised upstream dependencies are flagged
3. **Insider Threats:** Unauthorized changes by rogue employees are cryptographically provable
4. **CI/CD Hijacking:** Only verified commits trigger production deployments
