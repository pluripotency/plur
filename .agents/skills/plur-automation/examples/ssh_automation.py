#!/usr/bin/env python3
"""
ssh_automation.py - Remote SSH session automation with privilege escalation.
"""

from plur import base_node
from plur import session_wrap
from plur import base_shell

def run_ssh_workflow():
    # 1. Target node configuration
    node = base_node.Linux(
        hostname="target-server01",
        username="operator",
        password="operator_secure_pass",
        platform="almalinux9"
    )
    node.access_ip = "192.168.1.100"

    # 2. Wrap function in SSH session
    @session_wrap.ssh(node)
    def workflow(session):
        print(f"Connected to {session.hostname} as {session.username}")

        # Check disk space as operator
        df_out = base_shell.run(session, "df -h /")
        print("Disk space:\n", df_out)

        # Privilege escalation to root via su
        print("Escalating to root...")
        session.su(user="root")
        print(f"Current user: {base_shell.run(session, 'whoami')}")

        # Execute administrative command
        sys_status = base_shell.run(session, "systemctl is-active sshd")
        print("sshd status:", sys_status)

        # Return to operator user
        session.su_exit()
        print(f"Returned to user: {base_shell.run(session, 'whoami')}")

    workflow()

if __name__ == "__main__":
    run_ssh_workflow()
