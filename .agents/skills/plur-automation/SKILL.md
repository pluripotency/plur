---
name: plur-automation
description: >-
  Use this skill when developing CLI automation scripts, recipes, or tools using the plur library.
  Provides architecture guidance, Session and Node lifecycle patterns, base_shell commands, and decorators
  for local bash, SSH, and telnet automation.
---

# Plur CLI Automation Skill

`plur` is a Python library for automating interactive terminal/CLI operations (based on `pexpect` / pseudo-terminal `pty`).
It enables programmatic handling of SSH, Telnet, Bash shells, interactive prompts, command execution, and hierarchical sessions (jumpbox -> target host -> su/sudo).

---

## 1. Quick Reference: Core Components

| Module | Primary Role | Key Classes / Functions |
| :--- | :--- | :--- |
| [`plur.base_node`](file:///home/worker/Documents/antigravity/plur/plur/base_node.py) | Target definition & prompt detection | `Linux(hostname, username, password, platform)`, `Me()`, `Node(dict)` |
| [`plur.session`](file:///home/worker/Documents/antigravity/plur/plur/session.py) | Interactive pty session manager | `Session(node, log_params)`, `.run(cmd)`, `.su()`, `.sudo_i()`, `.ssh()`, `.close()` |
| [`plur.session_wrap`](file:///home/worker/Documents/antigravity/plur/plur/session_wrap.py) | Decorator-based session management | `@session_wrap.bash()`, `@session_wrap.ssh(node)`, `@session_wrap.telnet(node)` |
| [`plur.session_wrap_by_node_dict`](file:///home/worker/Documents/antigravity/plur/plur/session_wrap_by_node_dict.py) | Dictionary/Inventory-driven decorator | `@session_wrap_by_node_dict.ssh(node_dict)`, `@session_wrap_by_node_dict.bash(node_dict)` |
| [`plur.base_shell`](file:///home/worker/Documents/antigravity/plur/plur/base_shell.py) | Shell interaction utilities | `run(session, cmd)`, `here_doc(session, path, lines)`, `is_ping_ok(ip)(session)` |

---

## 2. Standard Usage Patterns

### Pattern A: Local Bash Automation (Decorator)
Use `@session_wrap.bash()` for automated tasks on the local machine (`base_node.Me()` is used by default).

```python
from plur import session_wrap
from plur import base_shell

def run_local_task():
    @session_wrap.bash()
    def recipe(session):
        # 1. Execute a command and capture stripped stdout
        output = base_shell.run(session, "uptime")
        print("Uptime:", output)

        # 2. Write a file using here_doc
        lines = ["# Generated config", "KEY=VALUE", "DEBUG=true"]
        base_shell.here_doc(session, "/tmp/sample_config.env", lines)

        # 3. Check connectivity
        if base_shell.is_ping_ok("127.0.0.1")(session):
            print("Localhost ping OK")

        return output

    return recipe()
```

### Pattern B: Remote SSH Automation (Object-based Node)
Define target server attributes via `base_node.Linux` and connect via `@session_wrap.ssh(node)`.

```python
from plur import base_node
from plur import session_wrap
from plur import base_shell

def inspect_remote_server():
    # Define remote Linux host
    node = base_node.Linux(
        hostname="web-prod-01",
        username="deployer",
        password="secret_password",
        platform="almalinux8"  # almalinux9, ubuntu, centos7, etc.
    )
    node.access_ip = "192.168.10.15"

    @session_wrap.ssh(node)
    def task(session):
        # Run command as deployer
        who = base_shell.run(session, "whoami")
        print("Logged in as:", who)

        # Privilege escalation to root via su
        session.su(user="root")
        root_who = base_shell.run(session, "whoami")
        print("Escalated to:", root_who)

        # Run root commands
        os_info = base_shell.run(session, "cat /etc/os-release")

        # Step down back to deployer
        session.su_exit()

        return os_info

    return task()
```

### Pattern C: Inventory / Dictionary-Driven Automation
Directly pass dictionaries from Host Credential Manager, JSON, or TOML inventory to `@session_wrap_by_node_dict.ssh`.

```python
from plur import session_wrap_by_node_dict
from plur import base_shell

host_inventory_item = {
    "hostname": "db-master.cluster",
    "access_ip": "10.0.0.21",
    "username": "admin",
    "password": "db_master_password",
    "platform": "ubuntu"
}

@session_wrap_by_node_dict.ssh(host_inventory_item)
def audit_db_host(session):
    df_output = base_shell.run(session, "df -h /")
    return df_output

result = audit_db_host()
print(result)
```

---

## 3. Session Stack Architecture (Hierarchical Navigation)

`Session` maintains a stack of nodes in `session.nodes`:
- **`session.push_node(node)`**: Pushes a new node onto the stack and updates `session.waitprompt` to match the new prompt.
- **`session.pop_node()`**: Pops the current node and restores the previous node's prompt pattern.
- **Nested Connections**:
  - Connect to Jumpbox -> SSH to internal host -> `su` to root -> `docker exec` / container.
  - Automatically restores prompt regex at each level on `pop_node()`.

---

## 4. Prompt Handling (`waitprompt`)

`plur` relies on regex prompt matching to determine when a command finishes:
- **AlmaLinux / RHEL / CentOS**: `r'\[?username@hostname .+\][\$#] '`
- **Ubuntu**: `r'username@hostname..+[\$#] '`
- If the shell uses a custom prompt, override `node.waitprompt` directly:
  ```python
  node.waitprompt = r'[\w-]+@[^ ]+:[^#$]+[#$] '
  ```

---

## 5. Detailed Documentation & Reference Files

Refer to the bundled references for in-depth technical details:
- [Architecture & Session Internals](./references/architecture.md): `Spawn`, `Session`, pty handling, logging, and exit handlers.
- [Base Shell API Catalog](./references/base_shell_api.md): Complete list of built-in functions in `plur.base_shell`.
- [Examples](./examples/):
  - [basic_bash.py](./examples/basic_bash.py): Local shell automation.
  - [ssh_automation.py](./examples/ssh_automation.py): Remote SSH and privilege escalation.
  - [hcm_integration.py](./examples/hcm_integration.py): Integration with Host Credential Manager.

---

## 6. Verification and Testing

When writing automation recipes with `plur`, verify using:
```bash
# Run plur unit tests
cd ../plur
python3 -m unittest discover test
```
