#!/bin/bash
# scripts/security-scan.sh - Comprehensive security scanning

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

echo "======================================"
echo "🔒 Atlantiplex Security Scan"
echo "======================================"

# 1. npm audit
log_info "Scanning Node.js dependencies..."
if npm audit --audit-level=moderate 2>&1 | grep -q "found"; then
    log_warn "npm vulnerabilities found (see above)"
else
    log_info "✅ npm audit passed"
fi

# 2. Check for hardcoded secrets
log_info "Scanning for hardcoded secrets..."
if git grep -E '(password|secret|token|key)\s*[:=]' -- '*.js' '*.py' 2>/dev/null | grep -v node_modules | grep -v test; then
    log_error "⚠️ Potential hardcoded secrets found (see above)"
else
    log_info "✅ No obvious hardcoded secrets"
fi

# 3. Check .env in git
log_info "Checking for .env files in git..."
if git ls-files | grep -E '\.env'; then
    log_error "❌ .env files committed to git (should only be .env.example)"
else
    log_info "✅ No .env files in git"
fi

# 4. Docker image scan (if Trivy installed)
if command -v trivy &> /dev/null; then
    log_info "Scanning Docker images with Trivy..."
    trivy image --severity HIGH,CRITICAL atlantiplex-stage:latest || log_warn "Trivy scan completed with warnings"
else
    log_warn "Trivy not installed. Install with: brew install aquasecurity/trivy/trivy"
fi

# 5. Check for insecure npm packages
log_info "Checking for known insecure packages..."
INSECURE_PACKAGES=("eval" "exec" "child_process" "require-from-url")
for pkg in "${INSECURE_PACKAGES[@]}"; do
    if npm ls "$pkg" 2>/dev/null | grep -q "├──"; then
        log_warn "Found potentially unsafe package: $pkg"
    fi
done

# 6. Python security (if available)
if command -v pip &> /dev/null; then
    log_info "Scanning Python dependencies..."
    if command -v safety &> /dev/null; then
        safety check 2>&1 || log_warn "Python safety check completed with warnings"
    fi
fi

# 7. Check Docker security
log_info "Checking Dockerfile security..."
for dockerfile in $(find . -name "Dockerfile*" -type f); do
    log_info "Checking $dockerfile"
    if grep -q "FROM.*:latest" "$dockerfile"; then
        log_warn "  ⚠️ Using :latest tag (use specific versions)"
    fi
    if grep -q "RUN.*sudo" "$dockerfile"; then
        log_error "  ❌ Using sudo in Dockerfile (run as non-root)"
    fi
    if ! grep -q "USER" "$dockerfile"; then
        log_warn "  ⚠️ No USER directive (should run as non-root)"
    fi
done

# 8. Check Kubernetes security
log_info "Checking Kubernetes manifests..."
for manifest in k8s/*.yaml; do
    if ! grep -q "runAsNonRoot: true" "$manifest"; then
        log_warn "  ⚠️ $manifest: runAsNonRoot not set"
    fi
    if ! grep -q "allowPrivilegeEscalation: false" "$manifest"; then
        log_warn "  ⚠️ $manifest: allowPrivilegeEscalation not set"
    fi
done

echo ""
echo "======================================"
echo "✅ Security scan complete!"
echo "======================================"
log_info "Review security report: SECURITY_VULNERABILITY_REMEDIATION.md"
