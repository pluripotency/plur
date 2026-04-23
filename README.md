# PLUR

PLUR is a Python-based CLI automation tool designed for managing interactive sessions and performing idempotent shell operations across various platforms. Built on top of `pexpect`, it provides a high-level API for handling SSH, Telnet, and local bash sessions with ease.

## Features

- **Session Management**: Easily manage nested sessions (SSH, Telnet, SU, SUDO) with a stack-based node architecture.
- **Idempotent Operations**: Built-in methods for common administrative tasks like file editing (`sed`), package management (`yum`), and service control, designed to be safe for repeated execution.
- **Cross-Platform Support**: Automatically detects and adapts to various Linux distributions including AlmaLinux, CentOS, and Ubuntu.
- **Interactive Automation**: Handle complex interactive prompts (passwords, SSH key confirmations) automatically using configurable expectation sequences.
- **Output Logging**: Comprehensive logging capabilities for debugging and capturing command output.

## Installation

PLUR uses `uv` for dependency management.

```bash
uv add git+https://github.com/pluripotency/plur
```

## Basic Usage

```python
from plur.session import Session
from plur.base_node import Node

# Define a target node
node = Node()
node.hostname = "example.com"
node.username = "admin"
node.password = "secret"

# Start a session
session = Session(node)
session.ssh()

# Run commands
session.run("ls -la")

# Elevate privileges
session.sudo_i()
session.run("apt update")

# Exit sessions
session.su_exit()
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
