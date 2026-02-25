# Automated Build Configuration - GitHub Authentication

## Problem
Build environment fails with:
```
fatal: could not read Username for 'https://github.com': terminal prompts disabled
```

## Solution for CI/CD & Automated Builds

### Option 1: Use Raw GitHub URLs (NO Authentication Needed) ⭐

**Docker Compose files available at:**
```
https://raw.githubusercontent.com/manticore22/atlantiplex-hub/main/docker-compose.prod.yml
https://raw.githubusercontent.com/manticore22/atlantiplex-hub/main/docker-compose.dev.yml
https://raw.githubusercontent.com/manticore22/atlantiplex-hub/main/docker-compose.yml
```

**In Docker Build or CI/CD:**
```dockerfile
# Download directly without authentication
RUN curl -o docker-compose.yml https://raw.githubusercontent.com/manticore22/atlantiplex-hub/main/docker-compose.prod.yml
RUN docker-compose -f docker-compose.yml up
```

Or in shell script:
```bash
#!/bin/bash
curl -o docker-compose.yml https://raw.githubusercontent.com/manticore22/atlantiplex-hub/main/docker-compose.prod.yml
docker-compose -f docker-compose.yml up
```

---

### Option 2: GitHub Personal Access Token (For Git Clone)

**Create Token:**
1. Go to: https://github.com/settings/tokens/new
2. Name: `build-token`
3. Scopes: ✓ repo, ✓ read:user
4. Generate and copy token

**Use in Build Environment:**

**Docker Build:**
```dockerfile
ARG GH_TOKEN
RUN git clone https://:${GH_TOKEN}@github.com/manticore22/atlantiplex-hub.git
```

Build command:
```bash
docker build --build-arg GH_TOKEN=ghp_xxx -t myapp .
```

**GitHub Actions:**
```yaml
- name: Clone Repository
  env:
    GH_TOKEN: ${{ secrets.GH_TOKEN }}
  run: |
    git clone https://:${GH_TOKEN}@github.com/manticore22/atlantiplex-hub.git
```

**GitLab CI:**
```yaml
clone_repo:
  script:
    - git clone https://:${CI_JOB_TOKEN}@github.com/manticore22/atlantiplex-hub.git
```

---

### Option 3: SSH Deploy Key (Most Secure for CI/CD)

**Generate SSH Key:**
```bash
ssh-keygen -t ed25519 -f deploy_key -N ""
```

**Add to GitHub:**
1. Go to: https://github.com/manticore22/atlantiplex-hub/settings/keys
2. Click "Add deploy key"
3. Paste `deploy_key.pub`
4. ✓ Allow write access

**Use in Build:**
```dockerfile
COPY deploy_key /root/.ssh/id_ed25519
RUN chmod 600 /root/.ssh/id_ed25519
RUN git clone git@github.com:manticore22/atlantiplex-hub.git
```

---

## Recommended: Raw GitHub URLs (Simplest)

Since authentication is disabled in your build environment, use **raw GitHub URLs** - no authentication needed:

```bash
# Direct download
curl -L https://raw.githubusercontent.com/manticore22/atlantiplex-hub/main/docker-compose.prod.yml -o docker-compose.yml

# Or with wget
wget https://raw.githubusercontent.com/manticore22/atlantiplex-hub/main/docker-compose.prod.yml

# Run
docker-compose up
```

**Available files:**
- Production: `docker-compose.prod.yml`
- Development: `docker-compose.dev.yml`
- Main: `docker-compose.yml`
- Testing: `docker-compose.test.yml`
- Hub: `docker-compose.hub.yml`

All at:
```
https://raw.githubusercontent.com/manticore22/atlantiplex-hub/main/[filename]
```

---

## For Docker Hub Automated Builds

If this is a Docker Hub build, configure in the repository settings:

**Docker Hub Build Configuration:**
1. Go to Repository → Build Settings
2. Configure Build Rules:
   ```
   Source Type: GitHub
   Source: main
   Docker Tag: latest
   Dockerfile location: Dockerfile
   Build Context: /
   ```

3. For accessing other files, use URLs in Dockerfile:
   ```dockerfile
   RUN curl https://raw.githubusercontent.com/manticore22/atlantiplex-hub/main/docker-compose.prod.yml
   ```

---

## Complete CI/CD Pipeline Example

### GitHub Actions
```yaml
name: Build and Test

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Download Docker Compose
        run: |
          curl -o docker-compose.yml \
            https://raw.githubusercontent.com/manticore22/atlantiplex-hub/main/docker-compose.prod.yml
      
      - name: Start Services
        run: docker-compose up -d
      
      - name: Run Tests
        run: docker-compose exec -T api npm test
      
      - name: Stop Services
        run: docker-compose down
```

### GitLab CI
```yaml
build_and_test:
  image: docker:latest
  services:
    - docker:dind
  script:
    - curl -o docker-compose.yml https://raw.githubusercontent.com/manticore22/atlantiplex-hub/main/docker-compose.prod.yml
    - docker-compose up -d
    - docker-compose exec -T api npm test
    - docker-compose down
```

### Jenkins
```groovy
pipeline {
    agent any
    stages {
        stage('Setup') {
            steps {
                sh '''
                    curl -o docker-compose.yml \
                      https://raw.githubusercontent.com/manticore22/atlantiplex-hub/main/docker-compose.prod.yml
                '''
            }
        }
        stage('Test') {
            steps {
                sh 'docker-compose up -d'
                sh 'docker-compose exec -T api npm test'
                sh 'docker-compose down'
            }
        }
    }
}
```

---

## Repository Files (Direct URLs)

**Main Docker Compose Files:**
| File | URL |
|------|-----|
| Production | https://raw.githubusercontent.com/manticore22/atlantiplex-hub/main/docker-compose.prod.yml |
| Development | https://raw.githubusercontent.com/manticore22/atlantiplex-hub/main/docker-compose.dev.yml |
| Default | https://raw.githubusercontent.com/manticore22/atlantiplex-hub/main/docker-compose.yml |
| Testing | https://raw.githubusercontent.com/manticore22/atlantiplex-hub/main/docker-compose.test.yml |

**Documentation:**
| File | URL |
|------|-----|
| Deployment Guide | https://raw.githubusercontent.com/manticore22/atlantiplex-hub/main/KUBERNETES_DEPLOYMENT_GUIDE.md |
| Package Index | https://raw.githubusercontent.com/manticore22/atlantiplex-hub/main/DEPLOYMENT_PACKAGE_INDEX.md |
| Kubernetes | https://raw.githubusercontent.com/manticore22/atlantiplex-hub/main/k8s/DEPLOYMENT_GUIDE.md |

**Environment Template:**
```
https://raw.githubusercontent.com/manticore22/atlantiplex-hub/main/.env.example
```

---

## Testing the URLs

Verify the files exist and are accessible:
```bash
# Test with curl
curl -I https://raw.githubusercontent.com/manticore22/atlantiplex-hub/main/docker-compose.prod.yml
# Should return: HTTP/2 200

# Download and verify
curl https://raw.githubusercontent.com/manticore22/atlantiplex-hub/main/docker-compose.prod.yml | head -20
# Should show docker-compose content
```

---

## Summary

**For your build issue:**
- ✅ Use raw GitHub URLs (no authentication needed)
- ✅ Download with `curl` or `wget`
- ✅ Run with `docker-compose up`

**Example one-liner:**
```bash
curl https://raw.githubusercontent.com/manticore22/atlantiplex-hub/main/docker-compose.prod.yml | docker-compose -f - up
```

**All files are public and accessible without authentication.**

---

**Status:** ✅ Ready for automated builds
**Repository:** https://github.com/manticore22/atlantiplex-hub
**Branch:** main
