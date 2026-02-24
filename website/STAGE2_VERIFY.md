Stage 2 Verification Checklist (Atlantiplex Studio)

1) Deploy sanity
- Stage 2 containers up and healthy (docker-compose stage2 ps)
- Nginx stage2 config loaded (nginx -t)

2) Access routes
- verilysovereign.org/atlantiplex/ loads the Atlantiplex Studio UI
- /api/health returns 200 OK from stage 1 and stage 2 endpoints

3) Admin panel
- Admin login page accessible via /admin-login.html
- Admin dashboard loads metrics from /api/admin/metrics

4) Auth flow
- Sign up at /signup.html
- Sign in at /login.html
- Admin created user or test admin user

5) Subscriptions
- Create a test paid subscription (use Stripe test keys) and verify the entitlement is recorded
- Verify /api/user/subscription returns tier for a test user

6) Atlantiplex gating
- If user not logged in, attempt to access Atlantiplex and verify redirection to login
- After login, verify that Atlantiplex route requires subscription when required by tier rules

7) Logs/Monitoring
- Check Nginx access & error logs for issues
- Check backend logs for errors

End of verification checklist.
