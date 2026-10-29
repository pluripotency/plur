#!/usr/bin/env python3
"""
basic_bash.py - Local Bash automation using plur.
"""

from plur import session_wrap
from plur import base_shell

def main():
    @session_wrap.bash()
    def task(session):
        print("=== 1. Checking Kernel & Hostname ===")
        uname = base_shell.run(session, "uname -a")
        print(f"Kernel info: {uname}")

        print("\n=== 2. Creating a temporary script with here_doc ===")
        script_path = "/tmp/plur_sample_test.sh"
        script_body = [
            "#!/bin/bash",
            "echo 'Hello from plur automated script'",
            "date +%Y-%m-%d_%H:%M:%S",
        ]
        base_shell.here_doc(session, script_path, script_body)
        base_shell.run(session, f"chmod +x {script_path}")

        print("\n=== 3. Executing the generated script ===")
        result = base_shell.run(session, script_path)
        print(f"Script output:\n{result}")

        print("\n=== 4. Cleaning up ===")
        base_shell.run(session, f"rm -f {script_path}")
        print("Cleanup done.")

    task()

if __name__ == "__main__":
    main()
