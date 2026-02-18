# Namecheap DNS wiring for verilysovereign.org

This document outlines the DNS configuration steps to bind www.verilysovereign.org to an Azure Static Web Apps (Path A MVP) and apex redirect via Namecheap.

1) Domain: verilysovereign.org
- Create a CNAME for www.verilysovereign.org -> <your-swa-hostname>.azurestaticwebapps.net
- Create an apex domain redirect: verilysovereign.org -> https://www.verilysovereign.org (301)
- Optional: TXT verification record provided by SWA when binding domain

2) Steps summary for Namecheap
- Add "www" CNAME to SWA hostname
- Add URL Redirect for apex (verilysovereign.org) to https://www.verilysovereign.org
- Bind the domain in Azure SWA and complete DNS verification
