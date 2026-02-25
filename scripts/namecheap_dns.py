#!/usr/bin/env python3
import os
import sys
import requests
import textwrap

NAMECHEAP_API_URL = "https://api.namecheap.com/xml.response"

def _build_set_hosts_params(domain: str, hosts: list, addresses: list, types: list, ttl: int = 60) -> dict:
    # Expect domain in the form example.com
    parts = domain.split(".")
    if len(parts) >= 2:
        sld = parts[-2]
        tld = parts[-1]
    else:
        raise ValueError("Invalid domain format for Namecheap DNS setHosts")

    api_user = os.environ.get("NAMECHEAP_USERNAME")
    api_key = os.environ.get("NAMECHEAP_API_KEY")
    client_ip = os.environ.get("NAMECHEAP_CLIENT_IP")
    if not all([api_user, api_key, client_ip]):
        raise RuntimeError("Missing Namecheap credentials in env (NAMECHEAP_USERNAME, NAMECHEAP_API_KEY, NAMECHEAP_CLIENT_IP)")

    params = {
        "ApiUser": api_user,
        "ApiKey": api_key,
        "UserName": api_user,
        "ClientIp": client_ip,
        "Command": "namecheap.domains.dns.setHosts",
        "SLD": sld,
        "TLD": tld,
    }

    for i, host in enumerate(hosts, start=1):
        params[f"HostName{i}"] = host
        params[f"RecordType{i}"] = types[i-1]
        params[f"Address{i}"] = addresses[i-1]
        params[f"TTL{i}"] = str(ttl)
    return params

def set_www_domain(www_host: str, swa_target: str) -> None:
    domain = www_host.split(".")[-2] + "." + www_host.split(".")[ -1]
    hosts = [www_host.split(".")[0]]  # 'www'
    types = ["CNAME"]
    addresses = [swa_target]

    domain_full = domain  # verilysovereign.org
    params = _build_set_hosts_params(domain_full, hosts, addresses, types)

    print("Submitting DNS update to Namecheap for:")
    print("Domain:", domain_full, "Host:", hosts[0], "Target:", swa_target)
    resp = requests.get(NAMECHEAP_API_URL, params=params, timeout=30)
    print("Namecheap response:", resp.text)

def main():
    domain = os.environ.get("NAMECHEAP_DOMAIN", "verilysovereign.org")
    swa_host = os.environ.get("SWA_HOSTNAME", "atlantiplex-studio-swa.azurestaticwebapps.net")
    www_domain = domain.replace("verily", "www" ) if domain.endswith("org") else f"www.{domain}"
    set_www_domain(www_host=www_domain, swa_target=swa_host)

if __name__ == "__main__":
    main()
