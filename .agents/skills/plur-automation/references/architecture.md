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

## 3. Node Stack & Prompt Management

When traversing multiple machines or subshells:

```
[Level 1: Me (Localhost)]
       |
       v session.push_node(remote_linux)
[Level 2: Remote Linux (worker@prod-app01)]
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
