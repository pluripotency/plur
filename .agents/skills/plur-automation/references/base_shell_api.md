# Base Shell API Reference (`references/base_shell_api.md`)

This reference lists the most useful functions available in `plur.base_shell`.

---

## 1. Core Execution

### `run(session, command)`
Sends `command` to the active shell session, captures stdout until the next prompt (`session.waitprompt`), strips terminal codes, and returns the result string.
```python
output = base_shell.run(session, "hostname -f")
```

### `capture_by_file_writer(file_path, write_mode='w')`
Decorator to redirect the captured output of an action to a dedicated local file.
```python
@base_shell.capture_by_file_writer("/tmp/command_output.txt")
def collect_logs(session):
    return base_shell.run(session, "journalctl -n 50")
```

---

## 2. File & Content Manipulation

### `here_doc(session, dst_file_path, contents, eof="'EOF'")`
Generates a `cat << 'EOF' > dst_file_path` command block to reliably write multiline text to a remote or local file.
```python
lines = [
    "server {",
    "    listen 80;",
    "    server_name example.com;",
    "}"
]
base_shell.here_doc(session, "/etc/nginx/conf.d/example.conf", lines)
```

### `heredoc_from_local(local_file_path, dst_file_path)`
Reads a local file on the runner machine and transfers its content to `dst_file_path` on the session machine via heredoc.

### `append_lines(session, file_path, lines)`
Appends a list of lines to a file.

### `idempotent_append(session, file_path, expression, line)`
Appends `line` to `file_path` only if `expression` is not already matched in the file (prevents duplicate entries in config files).

### `sed_replace(session, src_exp, dst_str, src_file, dst_file=None)`
Performs an in-place regex replacement using `sed`.

---

## 3. System Inspection & Testing

| Function | Signature / Usage | Description |
| :--- | :--- | :--- |
| `is_ping_ok` | `is_ping_ok(hostname_or_ip, count=2)(session)` | Returns `True` if ping succeeds, otherwise `False`. |
| `check_file_exists` | `check_file_exists(session, filename)` | Returns `True` if `test -f filename` passes. |
| `check_dir_exists` | `check_dir_exists(session, dir_path)` | Returns `True` if `test -d dir_path` passes. |
| `check_command_exists` | `check_command_exists(session, command)` | Returns `True` if `type command` passes. |
| `find_platform` | `find_platform(session)` | Inspects `/etc/redhat-release` and `/etc/issue` to detect OS distribution (`almalinux9`, `ubuntu`, `centos7`). |

---

## 4. Privilege Escalation & User Management

### `su(session, user='root')`
Switches user using `su - <user>` inside the interactive shell. Handles password prompt and updates the prompt matcher.

### `sudo_i(session)`
Executes `sudo -i`. Handles sudo password prompts and transitions to root shell.

### `configure_sudo(session, username)`
Adds passwordless sudo permissions for `username` via `/etc/sudoers.d/`.

---

## 5. Package & Service Management

### `yum_install(session, kwargs)`
Executes `yum -y install` or `dnf -y install` with automated confirmation handling.

### `service_on(session, service)` / `service_off(session, service)`
Controls systemd services (`systemctl start/enable` or `systemctl stop/disable`).
