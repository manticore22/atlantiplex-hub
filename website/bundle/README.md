Seraphonix Bundle Patch

Overview
- This patch bundle consolidates the brand-site and design-system into a ready-to-ship ZIP for handoff.
- The bundle includes: brand-site/, design-system/ with tokens, scripts to build tokens, and asset logos.

What to do
- This bundle now includes a Hostinger one-domain patch as an extension. You can generate the Hostinger patch ZIP with the new hostinger assemble script.
- Run the patch script to generate Seraphonix_Bundle.zip containing brand-site and design-system.
- Use the included deployment guide in the bundle to deploy to your hosting (Hostinger/Netlify/Vercel supported).

How to generate
- On Windows: run PowerShell script assemble-zip.ps1 from the bundle root.
- On other OS: run the provided assemble-zip.ps1 via PowerShell Core if available, or translate to a Bash script if needed.
