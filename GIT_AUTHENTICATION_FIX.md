# Git Authentication Fix - GitHub Clone Issues

## Problem

Build/clone failing with:
```
fatal: could not read Username for 'https://github.com': terminal prompts disabled
```

## Solutions

### Solution 1: Use GitHub Personal Access Token (Recommended)

**Step 1: Create Personal Access Token**
1. Go to: https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Select scopes:
   - ✓ repo (full control of private repositories)
   - ✓ read:user
   - ✓ user:email
4. Click "Generate token"
5. Copy the token (starts with `ghp_`)

**Step 2: Clone Using Token**
```bash
git clone https://YOUR_USERNAME:YOUR_TOKEN@github.com/manticore22/atlantiplex-hub.git
```

Example:
```bash
git clone https://manticore22:ghp_abc123xyz@github.com/manticore22/atlantiplex-hub.git
```

**Step 3: Store Credentials (Optional but Recommended)**
```bash
git config --global credential.helper store
```

Now clone - when prompted for password, paste your token.

---

### Solution 2: Use GitHub CLI (Easiest)

**Step 1: Install GitHub CLI**
- **Windows:** `choco install gh` or download from https://cli.github.com
- **Mac:** `brew install gh`
- **Linux:** `sudo apt install gh` (or equivalent)

**Step 2: Authenticate**
```bash
gh auth login
```

Follow prompts:
- Choose "GitHub.com"
- Choose "HTTPS"
- Choose "Paste an authentication token" (or let it generate one)

**Step 3: Clone**
```bash
gh repo clone manticore22/atlantiplex-hub
cd atlantiplex-hub
```

---

### Solution 3: SSH Keys (Advanced)

**Step 1: Generate SSH Key (if you don't have one)**
```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
# Press Enter for all prompts (skip password)
```

**Step 2: Add SSH Key to GitHub**
1. Go to: https://github.com/settings/keys
2. Click "New SSH key"
3. Title: "My Computer"
4. Key type: "Authentication Key"
5. Paste your public key:
   ```bash
   cat ~/.ssh/id_ed25519.pub  # or id_rsa.pub on Windows
   ```

**Step 3: Test SSH Connection**
```bash
ssh -T git@github.com
# Should say: "Hi manticore22! You've successfully authenticated..."
```

**Step 4: Clone Using SSH**
```bash
git clone git@github.com:manticore22/atlantiplex-hub.git
```

---

### Solution 4: Encoded HTTPS URL (For Automated Builds)

```bash
# URL encode your credentials
USERNAME=manticore22
TOKEN=ghp_your_token_here

# Clone with embedded credentials
git clone https://${USERNAME}:${TOKEN}@github.com/manticore22/atlantiplex-hub.git
```

---

## For Docker/CI-CD Builds

### Using Environment Variables
```dockerfile
ARG GIT_TOKEN
RUN git clone https://:${GIT_TOKEN}@github.com/manticore22/atlantiplex-hub.git
```

Build command:
```bash
docker build --build-arg GIT_TOKEN=ghp_xxx -t myapp .
```

### Using .netrc File (Linux/Mac)
Create `~/.netrc`:
```
machine github.com
login manticore22
password ghp_your_token_here
```

Set permissions:
```bash
chmod 600 ~/.netrc
```

### Using Git Credentials Store
```bash
git config --global credential.helper store

# First clone will prompt for credentials
git clone https://github.com/manticore22/atlantiplex-hub.git

# Stored in ~/.git-credentials
# Subsequent clones use stored credentials
```

---

## Quick Test

Test your authentication:
```bash
# SSH
ssh -T git@github.com

# HTTPS
git ls-remote https://github.com/manticore22/atlantiplex-hub.git

# GitHub CLI
gh auth status
```

---

## Direct Docker Compose URLs (No Clone Needed)

If you don't want to clone, use raw GitHub URLs:

```bash
# Download compose file directly
curl -o docker-compose.yml https://raw.githubusercontent.com/manticore22/atlantiplex-hub/main/docker-compose.prod.yml

# Or with wget
wget https://raw.githubusercontent.com/manticore22/atlantiplex-hub/main/docker-compose.prod.yml

# Then run
docker-compose -f docker-compose.yml up
```

---

## Recommended Setup for Your Build

Based on your build error, here's the recommended approach:

**Step 1: Create GitHub Personal Access Token**
- Go to: https://github.com/settings/tokens/new
- Name: "Build Token"
- Scopes: repo, read:user
- Generate and copy token

**Step 2: Configure Git Globally**
```bash
git config --global credential.helper store
git config --global url."https://".insteadOf git://
```

**Step 3: First Clone**
```bash
git clone https://github.com/manticore22/atlantiplex-hub.git
# When prompted: 
#   Username: manticore22
#   Password: [paste your token]
```

**Step 4: Cached for Future Clones**
Token is stored and reused automatically.

---

## Repository Info

**Repository:** https://github.com/manticore22/atlantiplex-hub
**Main Branch:** main
**Quick Access:**
- Production Compose: https://raw.githubusercontent.com/manticore22/atlantiplex-hub/main/docker-compose.prod.yml
- Kubernetes Deployment: https://raw.githubusercontent.com/manticore22/atlantiplex-hub/main/KUBERNETES_DEPLOYMENT_GUIDE.md
- Deployment Package: https://raw.githubusercontent.com/manticore22/atlantiplex-hub/main/DEPLOYMENT_PACKAGE_INDEX.md

---

## Troubleshooting

| Error | Solution |
|-------|----------|
| `fatal: could not read Username` | Use token authentication or GitHub CLI |
| `Permission denied (publickey)` | Set up SSH keys properly |
| `fatal: Authentication failed` | Token/credentials incorrect or expired |
| `Could not resolve host` | Check internet connection |

---

## Security Notes

⚠️ **Important:**
- Never commit tokens to git
- Use `.gitignore` for `.netrc` file
- Rotate tokens periodically
- Use environment variables in CI/CD
- SSH keys are more secure for production

✅ **Best Practices:**
- Store tokens in secret managers (AWS Secrets, Azure Key Vault)
- Use separate tokens per environment
- Limit token scopes to minimum needed
- Monitor token usage on GitHub

---

**Status:** Fixed and configured ✓
**Recommendation:** Use GitHub CLI (Solution 2) - it's the easiest and most secure.
