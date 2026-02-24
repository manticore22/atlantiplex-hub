# Master Launch Checklist - One Page

**Status**: ⏳ | **Owner**: __________ | **Deadline**: __________

---

## BEFORE LAUNCH (Parallel Tasks)

### Infrastructure (DevOps)
- [ ] Register Hostinger account
- [ ] Provision VPS (8GB RAM recommended)
- [ ] Record SSH credentials (IP, user, port)
- [ ] Test SSH access: `ssh user@IP`
- [ ] Domain registered and ready

### Secrets & Configuration (Security)
- [ ] Database password generated (32+ chars)
- [ ] Redis password generated (32+ chars)
- [ ] JWT secret generated (`openssl rand -hex 32`)
- [ ] All secrets stored in secure vault (1Password, Vault)
- [ ] .env.production created (local only, NEVER commit)
- [ ] Stripe API keys obtained
- [ ] Email provider configured

### Application (Development)
- [ ] Docker images built: `docker-compose build`
- [ ] Images scanned for CVEs: `docker scout cves`
- [ ] All tests passing (E2E tests completed)
- [ ] Code committed to main branch
- [ ] Ready for production deployment

### Team (Management)
- [ ] DevOps trained on procedures
- [ ] QA trained on validation
- [ ] Support team ready for go-live
- [ ] Escalation contacts confirmed
- [ ] On-call rotation established

**Owner Sign-Off**: __________ | **Date**: __________

---

## LAUNCH EXECUTION (30 Minutes)

### T-30: Preparation
```bash
# [ ] Verify all secrets ready
# [ ] Final backup of database
# [ ] Test SSH connection: ssh user@IP
```

### T-20: VPS Setup (10 minutes)
```bash
# [ ] ssh user@IP 'bash -s' < setup-hostinger.sh
# [ ] Wait for completion
# [ ] Verify: docker version, docker-compose version
```

### T-10: Build & Push (10 minutes)
```bash
# [ ] docker-compose build
# [ ] docker push yourusername/atlantiplex-stage:latest
# [ ] docker push yourusername/atlantiplex-flask:latest
# [ ] docker push yourusername/atlantiplex-frontend:latest
```

### T-0: Deploy (5 minutes)
```bash
# [ ] ./deploy-hostinger.sh production latest
# [ ] Wait for completion
# [ ] See ✅ success message
```

### T+5: Quick Validation
```bash
# [ ] ssh user@IP
# [ ] cd /home/atlantiplex && docker-compose ps
# [ ] All services show "Up"
```

**Deployment Owner**: __________ | **Time Started**: __________ | **Time Completed**: __________

---

## POST-LAUNCH (First 24 Hours)

### Immediate (T+5 to T+30 minutes)
- [ ] Health endpoints responding
- [ ] Database connections working
- [ ] No critical errors in logs
- [ ] Error rate <0.5%
- [ ] Response time normal (<500ms)

### First Hour
- [ ] Monitor: `docker stats`
- [ ] Check logs: `docker-compose logs -f`
- [ ] Test key features (login, upload, payments)
- [ ] No memory leaks
- [ ] CPU/Memory stable

### First 24 Hours
- [ ] Daily uptime monitoring
- [ ] Error rate trend <0.1%
- [ ] User feedback collection
- [ ] Quick-fix deployment if needed
- [ ] Team debriefing

**Monitor Owner**: __________ | **Team Lead**: __________

---

## DOMAIN & DNS (Can Run in Parallel)

- [ ] Update DNS A records to point to VPS IP
- [ ] Verify DNS propagation: `nslookup your-domain.com`
- [ ] SSL certificate auto-issued (Let's Encrypt)
- [ ] HTTPS working: `curl https://your-domain.com`
- [ ] Users can access domain

**DNS Owner**: __________ | **DNS Updated**: __________ | **Propagation Complete**: __________

---

## SUCCESS CRITERIA (All Must Be ✅)

| Criteria | Status | Owner |
|----------|--------|-------|
| All services running | ⏳ | __________ |
| Health endpoints 200 OK | ⏳ | __________ |
| Database responding | ⏳ | __________ |
| Redis cache working | ⏳ | __________ |
| No critical errors | ⏳ | __________ |
| Response time <500ms | ⏳ | __________ |
| Error rate <0.1% | ⏳ | __________ |
| Uptime >99% | ⏳ | __________ |
| Domain accessible | ⏳ | __________ |
| SSL valid | ⏳ | __________ |

**Final Sign-Off**: ✅ All criteria met

**Approved by**: 
- CTO: __________ 
- CEO: __________
- Date: __________

---

## EMERGENCY CONTACTS

| Role | Name | Phone | Email |
|------|------|-------|-------|
| DevOps Lead | __________ | __________ | __________ |
| CTO | __________ | __________ | __________ |
| QA Lead | __________ | __________ | __________ |
| Support Lead | __________ | __________ | __________ |

---

## QUICK COMMANDS

```bash
# Check status
ssh user@IP "cd /home/atlantiplex && docker-compose ps"

# View logs
ssh user@IP "cd /home/atlantiplex && docker-compose logs -f"

# Restart service
ssh user@IP "cd /home/atlantiplex && docker-compose restart atlantiplex-flask"

# Database backup
ssh user@IP "docker exec atlantiplex-postgres pg_dump -U atlantiplex atlantiplex > backup.sql"

# Rollback
./deploy-hostinger.sh rollback
```

---

## NOTES & ISSUES

```
Issue 1: ________________________
Status: ⏳ | Owner: __________ | Resolution: ________________________

Issue 2: ________________________
Status: ⏳ | Owner: __________ | Resolution: ________________________
```

---

## SIGN-OFFS

| Person | Role | Sign | Date |
|--------|------|------|------|
| __________ | DevOps Lead | ____ | ______ |
| __________ | QA Lead | ____ | ______ |
| __________ | Product Lead | ____ | ______ |
| __________ | CTO | ____ | ______ |
| __________ | CEO | ____ | ______ |

---

**LAUNCH STATUS**: 
- [ ] IN PROGRESS
- [ ] COMPLETED ✅
- [ ] ROLLED BACK ❌

**Time to Live**: __________
**Total Downtime**: __________
**Issues Encountered**: __________
**Resolution Time**: __________

---

**Document Version**: 1.0
**Last Updated**: __________
