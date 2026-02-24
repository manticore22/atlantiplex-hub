# Security Vulnerability Fixes - Implementation Checklist

## Priority 1: CRITICAL (Fix Immediately)

### 1. Dependency Vulnerabilities
- [ ] Run `npm audit` in all Node.js projects
- [ ] Run `pip install safety && safety check` for Python
- [ ] Fix all HIGH and CRITICAL vulnerabilities
- [ ] Update package*.json with secure versions
- [ ] Update requirements.txt with secure versions
- [ ] Test thoroughly after updates

**Action Items:**
```bash
# Node.js
cd apps/admin-dashboard && npm audit fix
cd apps/atlantiplex-studio && npm audit fix
cd apps/product-catalog && npm audit fix

# Python
pip install --upgrade -r requirements.txt
safety check
```

### 2. Hardcoded Secrets
- [ ] Remove all hardcoded secrets from code
- [ ] Never commit .env files (only .env.example)
- [ ] Use environment variables for all secrets
- [ ] Rotate all exposed credentials

**Files to check:**
```bash
grep -r "password\|secret\|token\|key" apps/ --include="*.js" --include="*.py" | grep -v test
grep -r "sk_live_\|sk_test_\|pk_live_" . --include="*.js" --include="*.py"
```

### 3. Docker Security
- [ ] Add `USER` directive to all Dockerfiles (non-root)
- [ ] Use specific version tags (not `:latest`)
- [ ] Add security context to all containers
- [ ] Remove unnecessary packages from images

**Example:**
```dockerfile
# Add to all Dockerfiles
RUN addgroup -g 1001 -S appuser && adduser -S appuser -u 1001
USER appuser
```

### 4. Kubernetes Security
- [ ] Verify all manifests have `runAsNonRoot: true`
- [ ] Verify `allowPrivilegeEscalation: false`
- [ ] Verify capabilities are dropped and minimized
- [ ] Apply network policies

---

## Priority 2: HIGH (Fix Within 1 Week)

### 5. Authentication & Authorization
- [ ] Implement JWT with short expiration (15 min access, 7 day refresh)
- [ ] Use bcrypt with 12+ rounds for password hashing
- [ ] Implement password strength validation
- [ ] Add rate limiting to login endpoints
- [ ] Implement token revocation/blacklist

**Sample Code:**
```javascript
// middleware/security.js already created - implement in your apps
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');

// Hash password
const hash = await bcrypt.hash(password, 12);

// Generate JWT
const token = jwt.sign(
  { userId, type: 'access' },
  process.env.JWT_SECRET,
  { algorithm: 'HS256', expiresIn: '15m' }
);
```

### 6. API Security
- [ ] Add rate limiting (100 req/15min general, 5 req/15min login)
- [ ] Implement input validation & sanitization
- [ ] Add Content Security Policy headers
- [ ] Implement CORS properly (whitelist domains)
- [ ] Add API key validation for webhooks

**Implementation:** See templates/NODE_SECURITY_CONFIG.js

### 7. Database Security
- [ ] Use parameterized queries everywhere
- [ ] Implement SQL injection prevention
- [ ] Add connection encryption (sslmode=require)
- [ ] Implement principle of least privilege for DB users
- [ ] Enable database audit logging

**Bad (Vulnerable):**
```javascript
const query = `SELECT * FROM users WHERE id = ${id}`;
```

**Good (Secure):**
```javascript
const query = 'SELECT * FROM users WHERE id = $1';
db.query(query, [id]);
```

### 8. Environment Variables
- [ ] Create .env.example with all required variables (no secrets)
- [ ] Document all environment variables
- [ ] Add validation for required variables
- [ ] Never log sensitive variables
- [ ] Rotate credentials regularly

**.env.example:**
```
NODE_ENV=production
DB_HOST=postgres
DB_PASSWORD=CHANGE_ME_16_CHARS_MIN
JWT_SECRET=CHANGE_ME_32_CHARS_MIN
REDIS_PASSWORD=CHANGE_ME_16_CHARS_MIN
CORS_ORIGIN=https://yourdomainhere.com
```

### 9. Logging & Monitoring
- [ ] Implement structured logging
- [ ] Never log passwords, tokens, API keys
- [ ] Log authentication failures
- [ ] Log authorization failures
- [ ] Set up log aggregation (ELK, Splunk, etc.)

**Example:**
```javascript
// Good - masks sensitive data
logger.info('Login attempt', { userId, email, timestamp });
// Bad - exposes password
logger.info('Login attempt', { userId, password, email });
```

### 10. HTTPS & TLS
- [ ] Enforce HTTPS (redirect HTTP to HTTPS)
- [ ] Use TLS 1.2+ only
- [ ] Implement HSTS header
- [ ] Get certificate from trusted CA (Let's Encrypt free)
- [ ] Set certificate renewal automation

---

## Priority 3: MEDIUM (Fix Within 2 Weeks)

### 11. Security Headers
- [ ] Add Helmet.js to Express apps
- [ ] Add Talisman to Flask apps
- [ ] Implement X-Frame-Options: DENY
- [ ] Implement X-Content-Type-Options: nosniff
- [ ] Implement Content-Security-Policy

Already implemented in templates - copy to your apps.

### 12. Dependency Management
- [ ] Add npm audit to CI/CD pipeline
- [ ] Add Snyk scanning to CI/CD
- [ ] Pin all dependencies to specific versions
- [ ] Regular dependency updates (monthly)
- [ ] Use lock files (package-lock.json, yarn.lock)

### 13. Secure Communication
- [ ] Implement request signing for webhooks
- [ ] Validate webhook signatures
- [ ] Use TLS for all external API calls
- [ ] Implement certificate pinning for critical APIs
- [ ] Validate SSL certificates

### 14. Error Handling
- [ ] Never expose stack traces in production
- [ ] Log errors securely
- [ ] Return generic error messages to clients
- [ ] Implement proper HTTP status codes
- [ ] Don't expose internal system details

### 15. CSRF Protection
- [ ] Implement CSRF tokens for forms
- [ ] Validate Same-Site cookie attribute
- [ ] Use POST for state-changing operations (not GET)
- [ ] Implement double-submit cookies pattern

---

## Priority 4: LOW (Fix Within 1 Month)

### 16. Security Scanning
- [ ] Set up Docker image scanning (Trivy, Snyk)
- [ ] Add SAST scanning to CI/CD (SonarQube, CodeQL)
- [ ] Add dependency scanning (Snyk, WhiteSource)
- [ ] Regular penetration testing
- [ ] Security code review process

### 17. Compliance & Documentation
- [ ] Document security architecture
- [ ] Create security incident response plan
- [ ] Document data handling procedures
- [ ] Create disaster recovery plan
- [ ] Create security runbooks

### 18. Infrastructure Security
- [ ] Enable VPC security groups
- [ ] Implement network segmentation
- [ ] Enable WAF (Web Application Firewall)
- [ ] Set up DDoS protection
- [ ] Enable CloudTrail/equivalent audit logging

### 19. Third-Party Services
- [ ] Verify Stripe PCI compliance
- [ ] Review all third-party integrations
- [ ] Ensure OAuth/OIDC security
- [ ] Verify data residency compliance
- [ ] Review data processing agreements

### 20. Incident Response
- [ ] Create security incident response plan
- [ ] Set up security monitoring & alerts
- [ ] Implement automated threat detection
- [ ] Create communication templates
- [ ] Conduct security drills quarterly

---

## Quick Implementation Scripts

### Run Security Scan
```bash
chmod +x scripts/security-scan.sh
./scripts/security-scan.sh
```

### Fix npm Vulnerabilities
```bash
npm audit fix
npm audit fix --audit-level=moderate --force
```

### Generate Package Lock Files
```bash
npm ci  # Install exact versions from package-lock.json
```

### Python Security Check
```bash
pip install safety pip-audit
safety check
pip-audit
```

---

## Testing Security Fixes

### Test Headers
```bash
curl -I https://yourdomain.com | grep -E "Strict-Transport|X-Content-Type|X-Frame"
```

### Test CORS
```bash
curl -H "Origin: http://example.com" -H "Access-Control-Request-Method: POST" -X OPTIONS https://yourdomain.com
```

### Test Rate Limiting
```bash
for i in {1..101}; do curl https://yourdomain.com/api/health; done
# Should get 429 status after limit
```

### Test SQL Injection Prevention
```bash
curl "https://yourdomain.com/api/user?id=1' OR '1'='1"
# Should get error, not data
```

---

## Files to Review

| File | Purpose |
|------|---------|
| SECURITY_VULNERABILITY_REMEDIATION.md | Comprehensive vulnerability guide |
| templates/NODE_SECURITY_CONFIG.js | Node.js/Express security middleware |
| templates/FLASK_SECURITY_CONFIG.py | Flask/Python security configuration |
| scripts/security-scan.sh | Automated security scanner |
| .env.example | Environment variables template |
| .gitignore | (Add secrets patterns) |
| k8s/\*.yaml | Security contexts verified |

---

## Resources

- OWASP Top 10 2023: https://owasp.org/Top10/
- Node.js Security: https://nodejs.org/en/docs/guides/security/
- Express.js Best Practices: https://expressjs.com/en/advanced/best-practice-security.html
- Flask Security: https://flask.palletsprojects.com/en/2.3.x/security/
- Docker Security: https://docs.docker.com/engine/security/
- Kubernetes Security: https://kubernetes.io/docs/concepts/security/
- npm Audit: https://docs.npmjs.com/cli/v6/commands/npm-audit
- Snyk: https://snyk.io/
- OWASP Cheat Sheet: https://cheatsheetseries.owasp.org/

---

## Sign-Off Checklist

- [ ] All CRITICAL vulnerabilities fixed
- [ ] All HIGH vulnerabilities fixed
- [ ] Security middleware implemented
- [ ] Rate limiting enabled
- [ ] Input validation added
- [ ] Security headers added
- [ ] HTTPS/TLS configured
- [ ] Environment variables secured
- [ ] Database queries parameterized
- [ ] Logging is secure (no PII)
- [ ] Authentication hardened (JWT, bcrypt)
- [ ] Kubernetes security contexts applied
- [ ] CI/CD security scanning enabled
- [ ] Security testing performed
- [ ] Security documentation created
- [ ] Team trained on security practices

---

**Start Date:** [TODAY]
**Target Completion:** [+2 weeks for P1&P2]
**Full Completion:** [+1 month for all priorities]

---

## Next Steps

1. Copy templates to your apps:
   ```bash
   cp templates/NODE_SECURITY_CONFIG.js apps/admin-dashboard/middleware/
   cp templates/FLASK_SECURITY_CONFIG.py matrix-studio/config/
   ```

2. Run security scan:
   ```bash
   ./scripts/security-scan.sh
   ```

3. Address HIGH/CRITICAL vulnerabilities first

4. Implement security middleware in apps

5. Test thoroughly

6. Deploy to production

Contact: security@atlantiplex.local
