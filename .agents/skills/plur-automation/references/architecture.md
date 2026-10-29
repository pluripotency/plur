# Plur Architecture & Internals (`references/architecture.md`)

This document details the internal design, object models, and execution flow of `plur`.

---

## 1. Class Hierarchy & Responsibilities

```
+-------------------------------------------------------+
|                       Spawn                           |
|  - Wraps pexpect.spawn (pty, encoding, timeouts)      |
|  - do(seq, timeout)                                   |
|  - action_handler(action, method_type)                |
|  - logger (Initialize, output_log, debug_log)         |
+-------------------------------------------------------+
                           ^
                           | inherits
+-------------------------------------------------------+
|                      Session                          |
|  - Manages node stack: session.nodes [Node, ...]      |
|  - push_node(node) / pop_node()                       |
|  - Shell entrypoints: .bash(), .ssh(), .telnet()      |
|  - Privilege escalation: .su(), .sudo_i(), .su_exit() |
|  - run(action) -> calls base_shell.run()              |
+-------------------------------------------------------+
```

---

## 2. The Execution Loop (`do` & `handle_output`)

`session.do(sequence)` is the fundamental primitive for interacting with a pseudo-terminal (pty):

```python
sequence = [
    action,       # Command string sent to pty (e.g. 'ls -l\n' or 'ssh ...')
    output_rows,  # Array of expectations: [[pattern, reaction, argument, description], ...]
    method_type   # 'sendline' (default), 'send', or 'sendcontrol'
]
```

### Flow in `handle_output`:
1. **`update_outputs(session, outputs)`**:
   - Injects `session.waitprompt` wherever `p_capture` or `waitprompt` is specified.
   - Maps `EOF` and `timeout` tokens to `pexpect.EOF` and `pexpect.TIMEOUT`.
2. **`session.child.expect(exout)`**:
   - Waits for one of the patterns to appear in the terminal output stream.
3. **Reaction Execution**:
   - `reaction` can be:
     - `p_capture`: Captures terminal output from the prompt.
     - `send_line`: Sends input and continues waiting.
     - `waitprompt`: Successfully terminates the command step.
     - Custom callable reaction functions.

---

## 3. Node Models & Prompt Management

### Available Node Classes (`plur.base_node`):
- **`SshNode(hostname, access_ip, username='worker', password='password', platform='almalinux9')`**:
  Dedicated node for SSH connections. Stores `access_ip` directly and automatically calculates `waitprompt` based on OS platform.
- **`create_linux_node(hostname, username='worker', password='password', platform='almalinux9', access_ip=None)`**:
  Factory function. If `access_ip` is provided, creates a node backed by `SSHConfig`, otherwise `BashConfig`.
- **`Linux(hostname, username, password, platform)`**:
  Generic Linux host definition.
- **`Me(platform=None)`**:
  Local machine node. Automatically detects OS platform, hostname, and current user via `detect_platform()`.
- **`SuNode(current_node, username='root')`**:
  Node representation when switching users via `su`.
- **`detect_platform()`**:
  Inspects `/etc/redhat-release` and `/etc/issue` to return the detected distribution (`almalinux10`, `almalinux9`, `almalinux8`, `centos7`, `centos6`, `ubuntu noble`, `ubuntu jammy`, `ubuntu`, `arch`).

When traversing multiple machines or subshells:

```
[Level 1: Me (Localhost)]
       |
       v session.push_node(remote_ssh_node)
[Level 2: SshNode (worker@prod-app01, access_ip=10.0.0.5)]
       |
       v session.su(user='root')
[Level 3: SuNode (root@prod-app01)]
```

- Each node provides `platform`, `hostname`, `username`, and `waitprompt`.
- On `push_node(node)`, `session.waitprompt` is dynamically updated.
- On `pop_node()`, the previous prompt is restored.

---

## 4. Logging & Debugging Subsystem

Plur includes a multi-channel logging system:
- **`output_log`**: Captures raw terminal pty bytes/strings. Can mirror to stdout (`enable_stdout: True`) and/or write to an output log file.
- **`debug_log`**: Records internal plur state changes, pattern matching decisions, and execution timing.
- **Log Parameters Dictionary**:
  ```python
  log_params = {
      'log_dir': '/tmp/plur_log',
      'enable_stdout': True,
      'output_log_file_path': '/tmp/plur_log/output.log',
      'debug_log_file_path': '/tmp/plur_log/debug.log',
      'debug_color': True,
      'dont_truncate': False,
  }
  ```

---

## 5. Pydantic Type & Validation System (`plur.types`)

As of `plur` v0.21, Pydantic v2 models are provided in `plur.types.node_types` and `plur.types.lib`:

### `SSHConfig`
```python
class SSHConfig(BaseModel):
    connection_type: Literal["ssh"] = "ssh"
    hostname: str
    username: str
    password: str = ""
    access_ip: ValidIpv4  # Validates IPv4 address string or ipaddress.IPv4Address
    platform: str

    @computed_field
    @property
    def waitprompt(self) -> str:
        return lib.get_linux_waitprompt(self.platform, self.hostname, self.username)
```

### `BashConfig`
```python
class BashConfig(BaseModel):
    connection_type: Literal["bash"] = "bash"
    hostname: str
    username: str
    password: str = ""
    platform: str

    @computed_field
    @property
    def waitprompt(self) -> str:
        return lib.get_linux_waitprompt(self.platform, self.hostname, self.username)
```

### `WorkerTarget` & `create_worker_target`
Validates worker target dictionaries and merges default account credentials before instantiating targets.
