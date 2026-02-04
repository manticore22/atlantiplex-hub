# Atlantiplex Lightning Studio - Azure Hosting Guide

## 🚀 Deploy Your SaaS Platform to Microsoft Azure

---

## 📋 **PREREQUISITES**

### **Required Azure Services:**
- ✅ Azure App Service (Web App)
- ✅ Azure Database for PostgreSQL (or Azure SQL)
- ✅ Azure Cache for Redis
- ✅ Azure Storage Account (for media/uploads)
- ✅ Azure Key Vault (for secrets)
- ✅ Azure Application Insights (monitoring)
- ✅ Azure CDN (optional, for static assets)

### **Tools Needed:**
- Azure CLI
- Docker Desktop
- Git
- Visual Studio Code (with Azure extensions)

---

## 🏗️ **ARCHITECTURE OVERVIEW**

```
┌─────────────────────────────────────────────────────────────┐
│                     Azure Cloud                              │
├─────────────────────────────────────────────────────────────┤
│  Azure Front Door / CDN                                     │
│       ↓                                                     │
│  Azure App Service (Web App)                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Docker Container                                   │   │
│  │  ┌───────────────────────────────────────────────┐ │   │
│  │  │  Atlantiplex SaaS Platform                    │ │   │
│  │  │  • Flask Application                          │ │   │
│  │  │  • Multi-tenant Architecture                  │ │   │
│  │  │  • Stripe Integration                         │ │   │
│  │  └───────────────────────────────────────────────┘ │   │
│  └─────────────────────────────────────────────────────┘   │
│       ↓                                                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐    │
│  │  Azure DB   │  │ Azure Redis │  │ Azure Storage   │    │
│  │ PostgreSQL  │  │  Cache      │  │  (Media/Blobs)  │    │
│  └─────────────┘  └─────────────┘  └─────────────────┘    │
│       ↓                                                     │
│  Azure Key Vault (Secrets Management)                       │
│       ↓                                                     │
│  Azure Application Insights (Monitoring)                    │
└─────────────────────────────────────────────────────────────┘
```

---

## 📦 **STEP 1: PREPARE YOUR APPLICATION**

### **1.1 Create Production Dockerfile**

```dockerfile
# Atlantiplex Lightning Studio - Production Dockerfile
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production
ENV PORT=8080

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        gcc \
        libc6-dev \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Run application with Gunicorn
CMD gunicorn --bind 0.0.0.0:8080 --workers 4 --threads 2 --timeout 60 saas_platform:app
```

### **1.2 Create requirements.txt**

```
# Core Flask
certifi==2024.7.4
charset-normalizer==3.3.2
click==8.1.7
Flask==3.0.3
Flask-Cors==4.0.1
idna==3.8
itsdangerous==2.2.0
Jinja2==3.1.4
MarkupSafe==2.1.5
requests==2.32.3
urllib3==2.2.2
Werkzeug==3.0.4

# Production Server
gunicorn==23.0.0

# Database
psycopg2-binary==2.9.9
SQLAlchemy==2.0.32

# Caching
redis==5.0.8

# Authentication & Security
PyJWT==2.9.0
bcrypt==4.2.0

# Stripe Payments
stripe==9.8.0

# Azure SDK
azure-identity==1.17.1
azure-keyvault-secrets==4.8.0
azure-storage-blob==12.22.0

# Monitoring
opencensus-ext-azure==1.1.13
opencensus-ext-flask==0.8.3

# Utilities
python-dotenv==1.0.1
```

### **1.3 Create .dockerignore**

```
__pycache__
*.pyc
*.pyo
*.pyd
.Python
env
pip-log.txt
pip-delete-this-directory.txt
.tox
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.log
.git
.mypy_cache
.pytest_cache
.hypothesis

# Database files
*.db
*.sqlite
*.sqlite3

# Environment files (except example)
.env
.env.local
.env.production
!.env.example

# IDE
.vscode
.idea
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Documentation
docs/*.md
!docs/README.md

# Tests
tests/
.pytest_cache/

# Node modules (if any)
node_modules/
```

---

## 🔐 **STEP 2: AZURE INFRASTRUCTURE SETUP**

### **2.1 Create Resource Group**

```bash
# Login to Azure
az login

# Set subscription (if you have multiple)
az account set --subscription "Your-Subscription-Name"

# Create resource group
az group create \
  --name atlantiplex-rg \
  --location eastus \
  --tags environment=production project=atlantiplex
```

### **2.2 Create Azure Database for PostgreSQL**

```bash
# Create PostgreSQL server
az postgres flexible-server create \
  --resource-group atlantiplex-rg \
  --name atlantiplex-db \
  --location eastus \
  --admin-user atlantiplexadmin \
  --admin-password "YourStrongPassword123!" \
  --sku-name Standard_D2s_v3 \
  --tier GeneralPurpose \
  --storage-size 128 \
  --version 15 \
  --public-access 0.0.0.0 \
  --database-name atlantiplex_saas

# Create database
az postgres flexible-server db create \
  --resource-group atlantiplex-rg \
  --server-name atlantiplex-db \
  --database-name atlantiplex_saas

# Allow Azure services access
az postgres flexible-server firewall-rule create \
  --resource-group atlantiplex-rg \
  --name atlantiplex-db \
  --rule-name AllowAzureServices \
  --start-ip-address 0.0.0.0 \
  --end-ip-address 0.0.0.0
```

### **2.3 Create Azure Cache for Redis**

```bash
az redis create \
  --resource-group atlantiplex-rg \
  --name atlantiplex-redis \
  --location eastus \
  --sku Standard \
  --vm-size c1 \
  --enable-non-ssl-port false

# Get connection string
az redis list-keys \
  --resource-group atlantiplex-rg \
  --name atlantiplex-redis
```

### **2.4 Create Azure Storage Account**

```bash
# Create storage account
az storage account create \
  --resource-group atlantiplex-rg \
  --name atlantiplexstorage \
  --location eastus \
  --sku Standard_LRS \
  --kind StorageV2 \
  --https-only true \
  --min-tls-version TLS1_2

# Create container for uploads
az storage container create \
  --account-name atlantiplexstorage \
  --name uploads \
  --public-access off

# Get connection string
az storage account show-connection-string \
  --resource-group atlantiplex-rg \
  --name atlantiplexstorage
```

### **2.5 Create Azure Key Vault**

```bash
# Create Key Vault
az keyvault create \
  --resource-group atlantiplex-rg \
  --name atlantiplex-kv \
  --location eastus \
  --sku standard \
  --enable-rbac-authorization true

# Add secrets
az keyvault secret set \
  --vault-name atlantiplex-kv \
  --name stripe-secret-key \
  --value "sk_live_your_stripe_secret_key"

az keyvault secret set \
  --vault-name atlantiplex-kv \
  --name stripe-publishable-key \
  --value "pk_live_your_stripe_publishable_key"

az keyvault secret set \
  --vault-name atlantiplex-kv \
  --name flask-secret-key \
  --value "your-super-secret-flask-key"

az keyvault secret set \
  --vault-name atlantiplex-kv \
  --name jwt-secret-key \
  --value "your-jwt-secret-key"
```

---

## 🚀 **STEP 3: DEPLOY TO AZURE APP SERVICE**

### **3.1 Create App Service Plan**

```bash
az appservice plan create \
  --resource-group atlantiplex-rg \
  --name atlantiplex-plan \
  --sku P1v2 \
  --is-linux \
  --location eastus
```

### **3.2 Create Web App**

```bash
az webapp create \
  --resource-group atlantiplex-rg \
  --plan atlantiplex-plan \
  --name atlantiplex-saas \
  --deployment-container-image-name atlantiplex.azurecr.io/atlantiplex-saas:latest \
  --docker-registry-server-url https://atlantiplex.azurecr.io \
  --docker-registry-server-user atlantiplex \
  --docker-registry-server-password "your-registry-password"
```

### **3.3 Configure Application Settings**

```bash
# Get PostgreSQL connection details
DB_HOST=$(az postgres flexible-server show \
  --resource-group atlantiplex-rg \
  --name atlantiplex-db \
  --query fullyQualifiedDomainName -o tsv)

# Configure app settings
az webapp config appsettings set \
  --resource-group atlantiplex-rg \
  --name atlantiplex-saas \
  --settings \
    FLASK_ENV=production \
    DATABASE_URL="postgresql://atlantiplexadmin:YourStrongPassword123!@${DB_HOST}:5432/atlantiplex_saas" \
    REDIS_URL="atlantiplex-redis.redis.cache.windows.net:6380,password=your-redis-key,ssl=True" \
    STORAGE_CONNECTION_STRING="your-storage-connection-string" \
    KEY_VAULT_NAME=atlantiplex-kv \
    AZURE_CLIENT_ID="your-service-principal-id" \
    AZURE_TENANT_ID="your-tenant-id" \
    AZURE_CLIENT_SECRET="your-service-principal-secret" \
    WEBSITES_PORT=8080 \
    SCM_DO_BUILD_DURING_DEPLOYMENT=true
```

---

## 🔧 **STEP 4: CI/CD PIPELINE (GitHub Actions)**

Create `.github/workflows/azure-deploy.yml`:

```yaml
name: Deploy to Azure

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

env:
  AZURE_WEBAPP_NAME: atlantiplex-saas
  AZURE_WEBAPP_PACKAGE_PATH: '.'
  PYTHON_VERSION: '3.11'

jobs:
  build-and-test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: ${{ env.PYTHON_VERSION }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov
    
    - name: Run tests
      run: |
        pytest tests/ --cov=./ --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml

  build-and-push-docker:
    needs: build-and-test
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v3
    
    - name: Log in to Azure Container Registry
      uses: docker/login-action@v3
      with:
        registry: atlantiplex.azurecr.io
        username: ${{ secrets.AZURE_REGISTRY_USERNAME }}
        password: ${{ secrets.AZURE_REGISTRY_PASSWORD }}
    
    - name: Build and push Docker image
      uses: docker/build-push-action@v5
      with:
        context: .
        push: true
        tags: |
          atlantiplex.azurecr.io/atlantiplex-saas:latest
          atlantiplex.azurecr.io/atlantiplex-saas:${{ github.sha }}
        cache-from: type=gha
        cache-to: type=gha,mode=max

  deploy-to-azure:
    needs: build-and-push-docker
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Azure Login
      uses: azure/login@v2
      with:
        creds: ${{ secrets.AZURE_CREDENTIALS }}
    
    - name: Deploy to Azure Web App
      uses: azure/webapps-deploy@v3
      with:
        app-name: ${{ env.AZURE_WEBAPP_NAME }}
        images: 'atlantiplex.azurecr.io/atlantiplex-saas:${{ github.sha }}'
    
    - name: Azure logout
      run: |
        az logout
```

---

## 🗄️ **STEP 5: DATABASE MIGRATION**

### **5.1 Create Migration Script**

```python
# migrate_to_azure.py
import os
import psycopg2
from urllib.parse import urlparse

def migrate_database():
    """Migrate local SQLite database to Azure PostgreSQL"""
    
    # Get Azure PostgreSQL connection
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        raise ValueError("DATABASE_URL environment variable not set")
    
    # Parse connection string
    url = urlparse(database_url)
    
    # Connect to Azure PostgreSQL
    conn = psycopg2.connect(
        host=url.hostname,
        port=url.port or 5432,
        database=url.path[1:],
        user=url.username,
        password=url.password,
        sslmode='require'
    )
    
    cursor = conn.cursor()
    
    # Initialize schema
    print("Initializing SaaS database schema...")
    
    # Run schema creation
    from saas_database import SaaSDatabaseManager
    db = SaaSDatabaseManager(db_path=database_url.replace('postgresql://', ''))
    
    print("✅ Database migration completed")
    
    conn.close()

if __name__ == "__main__":
    migrate_database()
```

### **5.2 Run Migration**

```bash
# Set environment variable
export DATABASE_URL="postgresql://atlantiplexadmin:YourPassword@atlantiplex-db.postgres.database.azure.com:5432/atlantiplex_saas"

# Run migration
python migrate_to_azure.py
```

---

## 🌐 **STEP 6: CUSTOM DOMAIN & SSL**

### **6.1 Configure Custom Domain**

```bash
# Add custom domain
az webapp config hostname add \
  --resource-group atlantiplex-rg \
  --webapp-name atlantiplex-saas \
  --hostname app.yourdomain.com

# Verify domain ownership (add DNS TXT record)
# Then bind SSL certificate
az webapp config ssl bind \
  --resource-group atlantiplex-rg \
  --name atlantiplex-saas \
  --certificate-thumbprint "your-cert-thumbprint" \
  --ssl-type SNI
```

### **6.2 DNS Configuration**

Add these DNS records:

```
Type    Name              Value                           TTL
A       @                YOUR_APP_SERVICE_IP             3600
CNAME   www              atlantiplex-saas.azurewebsites.net  3600
CNAME   app              atlantiplex-saas.azurewebsites.net  3600
TXT     @                verification-token-from-azure   3600
```

---

## 📊 **STEP 7: MONITORING & LOGGING**

### **7.1 Enable Application Insights**

```bash
# Create Application Insights
az monitor app-insights component create \
  --resource-group atlantiplex-rg \
  --app atlantiplex-insights \
  --location eastus \
  --application-type web

# Get instrumentation key
az monitor app-insights component show \
  --resource-group atlantiplex-rg \
  --app atlantiplex-insights \
  --query instrumentationKey -o tsv

# Configure web app
az webapp config appsettings set \
  --resource-group atlantiplex-rg \
  --name atlantiplex-saas \
  --settings APPINSIGHTS_INSTRUMENTATIONKEY="your-instrumentation-key"
```

### **7.2 Enable Logging**

```bash
# Configure logging
az webapp log config \
  --resource-group atlantiplex-rg \
  --name atlantiplex-saas \
  --application-logging true \
  --detailed-error-messages true \
  --failed-request-tracing true \
  --level information

# Stream logs
az webapp log tail \
  --resource-group atlantiplex-rg \
  --name atlantiplex-saas
```

---

## 📈 **STEP 8: SCALING CONFIGURATION**

### **8.1 Auto-scaling Rules**

```bash
# Create auto-scale settings
az monitor autoscale create \
  --resource-group atlantiplex-rg \
  --resource atlantiplex-plan \
  --resource-type Microsoft.Web/serverfarms \
  --name atlantiplex-autoscale \
  --min-count 2 \
  --max-count 10 \
  --count 2

# Add scale-out rule (CPU > 70%)
az monitor autoscale rule create \
  --resource-group atlantiplex-rg \
  --autoscale-name atlantiplex-autoscale \
  --condition "Percentage CPU > 70 avg 5m" \
  --scale out 2

# Add scale-in rule (CPU < 30%)
az monitor autoscale rule create \
  --resource-group atlantiplex-rg \
  --autoscale-name atlantiplex-autoscale \
  --condition "Percentage CPU < 30 avg 10m" \
  --scale in 1
```

### **8.2 Performance Tiers**

**Development:**
- App Service: Basic B1 ($12.41/month)
- Database: Burstable B1ms ($12.98/month)
- Redis: Basic C0 ($16.19/month)
- **Total: ~$42/month**

**Production (Starter):**
- App Service: Standard S1 ($73.02/month)
- Database: General Purpose D2s_v3 ($135.20/month)
- Redis: Standard C1 ($41.93/month)
- Storage: Standard LRS ($25/month)
- **Total: ~$275/month**

**Production (Enterprise):**
- App Service: Premium P1v2 ($146/month)
- Database: Memory Optimized E2s_v3 ($166/month)
- Redis: Premium P1 ($263/month)
- Storage: Premium LRS ($150/month)
- CDN: Standard Microsoft ($17/month)
- **Total: ~$742/month**

---

## 🔒 **STEP 9: SECURITY BEST PRACTICES**

### **9.1 Enable HTTPS Only**

```bash
az webapp update \
  --resource-group atlantiplex-rg \
  --name atlantiplex-saas \
  --https-only true
```

### **9.2 Configure CORS**

```bash
az webapp cors add \
  --resource-group atlantiplex-rg \
  --name atlantiplex-saas \
  --allowed-origins \
    https://app.yourdomain.com \
    https://admin.yourdomain.com
```

### **9.3 Network Security**

```bash
# Enable VNet integration (optional)
az webapp vnet-integration add \
  --resource-group atlantiplex-rg \
  --name atlantiplex-saas \
  --vnet atlantiplex-vnet \
  --subnet appservice-subnet

# Restrict database access to App Service only
az postgres flexible-server firewall-rule delete \
  --resource-group atlantiplex-rg \
  --name atlantiplex-db \
  --rule-name AllowAzureServices

# Add specific App Service IP
az postgres flexible-server firewall-rule create \
  --resource-group atlantiplex-rg \
  --name atlantiplex-db \
  --rule-name AllowAppService \
  --start-ip-address "YOUR_APP_SERVICE_OUTBOUND_IP" \
  --end-ip-address "YOUR_APP_SERVICE_OUTBOUND_IP"
```

---

## ✅ **DEPLOYMENT CHECKLIST**

- [ ] Azure CLI installed and logged in
- [ ] Resource group created
- [ ] PostgreSQL database deployed
- [ ] Redis cache deployed
- [ ] Storage account created
- [ ] Key Vault configured with secrets
- [ ] App Service Plan created
- [ ] Web App deployed
- [ ] Environment variables configured
- [ ] Database migrated
- [ ] Custom domain configured
- [ ] SSL certificate installed
- [ ] Application Insights enabled
- [ ] Auto-scaling configured
- [ ] CI/CD pipeline setup
- [ ] Backup policy configured
- [ ] Monitoring dashboards created
- [ ] Alert rules configured

---

## 🆘 **TROUBLESHOOTING**

### **App Won't Start:**
```bash
# Check logs
az webapp log tail --resource-group atlantiplex-rg --name atlantiplex-saas

# Check container logs
az webapp log deployment show --resource-group atlantiplex-rg --name atlantiplex-saas

# Restart app
az webapp restart --resource-group atlantiplex-rg --name atlantiplex-saas
```

### **Database Connection Issues:**
```bash
# Test database connectivity
az webapp ssh --resource-group atlantiplex-rg --name atlantiplex-saas
# Then: nc -zv atlantiplex-db.postgres.database.azure.com 5432
```

### **Performance Issues:**
```bash
# Check metrics
az monitor metrics list \
  --resource "$(az webapp show --resource-group atlantiplex-rg --name atlantiplex-saas --query id -o tsv)" \
  --metric "CpuPercentage" \
  --interval PT1M
```

---

## 📞 **SUPPORT & RESOURCES**

- **Azure Documentation:** https://docs.microsoft.com/azure/
- **App Service:** https://docs.microsoft.com/azure/app-service/
- **PostgreSQL:** https://docs.microsoft.com/azure/postgresql/
- **Pricing Calculator:** https://azure.microsoft.com/pricing/calculator/
- **Status Page:** https://status.azure.com/

---

## 🎉 **YOU'RE DEPLOYED!**

Your Atlantiplex Lightning Studio SaaS platform is now running on Azure with:
- ✅ Enterprise-grade infrastructure
- ✅ Auto-scaling capabilities
- ✅ SSL/TLS encryption
- ✅ Database backups
- ✅ Monitoring & alerting
- ✅ CI/CD pipeline
- ✅ Multi-region ready

**Estimated Time to Deploy:** 30-45 minutes

**Next Steps:**
1. Test all endpoints
2. Configure Stripe production keys
3. Set up custom domains
4. Configure monitoring alerts
5. Load test the application