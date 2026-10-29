#!/usr/bin/env python3
"""
hcm_integration.py - Direct integration with Host Credential Manager (HCM) dictionary inventory.
"""

from plur import session_wrap_by_node_dict
from plur import base_shell

def audit_host_from_hcm_inventory(host_record):
    """
    Accepts a dictionary compatible with Host Credential Manager / JSON export:
    {
        "hostname": "...",
        "access_ip": "...",  # or "ip"
        "username": "...",
        "password": "...",
        "platform": "almalinux8" / "ubuntu"
    }
    """
    # Normalize access_ip if key is "ip"
    if "ip" in host_record and "access_ip" not in host_record:
        host_record["access_ip"] = host_record["ip"]

    @session_wrap_by_node_dict.ssh(host_record)
    def audit_task(session):
        print(f"[*] Auditing host: {session.hostname} ({host_record.get('access_ip')})")
        uptime = base_shell.run(session, "uptime")
        mem = base_shell.run(session, "free -m")
        return {
            "hostname": session.hostname,
            "uptime": uptime,
            "memory": mem,
        }

    return audit_task()

if __name__ == "__main__":
    sample_hcm_host = {
        "hostname": "web-prod-01",
        "ip": "127.0.0.1",
        "username": "worker",
        "password": "sample_password",
        "platform": "almalinux9"
    }
    # For testing, you can execute against a live host
    print("Ready to run against:", sample_hcm_host["hostname"])
