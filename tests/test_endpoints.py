#!/usr/bin/env python3
import json
import urllib.request
import pathlib
import sys

def check_url(url, timeout=5):
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            code = resp.getcode()
            return True if 200 <= code < 300 else False, code
    except Exception as e:
        return False, str(e)

endpoints = [
    "http://verilysovereign.online/health",
    "http://verilysovereign.online/api/health",
    "http://website.verilysovereign.online/health",
    "http://studio.verilysovereign.online/health",
]

results = []
for url in endpoints:
    ok, info = check_url(url)
    results.append({"url": url, "ok": ok, "info": info})

summary = {
    "ok": all(r.get("ok", False) for r in results),
    "results": results,
}

summary_path = pathlib.Path("test_endpoints_summary.json")
summary_path.write_text(json.dumps(summary, indent=2))
print(json.dumps(summary, indent=2))

if not summary["ok"]:
    sys.exit(1)
