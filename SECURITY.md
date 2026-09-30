# Security Policy

## Supported Versions

Kommand is currently under active development.

| Version | Supported |
| ------- | --------- |
| `1.x.x` | Yes       |

Security fixes are applied to supported release lines where practical. Users should run the latest available release whenever possible.

---

## Reporting a Vulnerability

**Please do not open a public GitHub issue for security vulnerabilities.**

If you believe you have discovered a security vulnerability in Kommand, report it privately:

**Email:** [security@kommand.dev](mailto:security@kommand.dev)

### What to Include

Please provide as much of the following information as possible:

- A clear description of the vulnerability
- The affected Kommand version
- The affected Linux distribution and version
- The affected component, domain, adapter, plugin, or command
- Steps to reproduce the issue
- Potential security impact
- Proof-of-concept code or commands, if available
- Suggested mitigation or fix, if you have one

For example:

```text
Kommand version: 1.0.0
Distribution: Fedora 42
Python version: 3.12

Component:
domains/services/

Description:
...

Steps to reproduce:
1. ...
2. ...
3. ...

Expected behavior:
...

Actual behavior:
...

Potential impact:
...
```

### Response Timeline

We aim to:

- Acknowledge vulnerability reports within **72 hours**
- Assess the severity and scope of the report
- Keep the reporter informed during investigation where appropriate
- Release a fix for critical vulnerabilities within **14 days** when practical

Response and remediation timelines may vary depending on the complexity of the vulnerability, availability of a safe fix, affected platforms, and whether coordinated disclosure is required.

---

## Security Design

Security and privacy are core design requirements of Kommand.

### No Telemetry

Kommand does not intentionally collect telemetry or send usage information to remote services.

Kommand is designed to operate locally without outbound network communication as part of normal system-management operations. Outbound network calls are made only when a user explicitly initiates an action that requires one, such as checking for package or firmware updates.

Any future feature that requires network communication must be explicitly documented and reviewed as part of its security design.

### Credential Handling

Sudo passwords and other sensitive credentials must never be:

- Written to log files
- Stored in configuration files
- Included in error messages
- Included in telemetry
- Printed to the terminal
- Persisted by Kommand

Authentication credentials must only be handled for the minimum amount of time required to perform the requested privileged operation.

### Safe Command Execution

System commands are executed using argument lists rather than shell command strings.

Kommand must **not** construct privileged commands through unsafe string interpolation.

For example, commands should conceptually follow this pattern:

```python
subprocess.run(
    ["systemctl", "restart", service_name],
    check=True,
)
```

rather than constructing a shell command from user-controlled input.

The use of `shell=True` is prohibited unless a specific, documented security review establishes that it is necessary and safe.

### Input Validation

User-controlled values must be validated before being passed to system commands or other security-sensitive operations.

This includes, where applicable:

- File paths
- Service names
- User and group names
- Package names
- Interface names
- Configuration values
- Plugin-provided values
- CLI arguments

Validation should occur at the appropriate domain or infrastructure boundary rather than relying on downstream system commands to reject unsafe input.

### Privilege Escalation

Kommand follows a **least-privilege** approach.

Privileged operations should request elevation only when the individual operation requires it.

Kommand must not require the entire application to run permanently as root.

The privilege-management layer is responsible for detecting and handling elevation requirements rather than individual domain modules implementing their own privilege mechanisms.

The intended model is:

```text
Normal application
       │
       ├── Non-privileged operation
       │       └── Execute normally
       │
       └── Privileged operation
               └── Request elevation for that action
```

This reduces the amount of application code executing with elevated privileges.

### Plugin Safety

Kommand supports plugins, including community-developed plugins.

Plugin failures must not be allowed to crash the host application.

Plugin execution is isolated at the application boundary so that exceptions and other plugin failures can be handled without terminating Kommand.

However, application-level exception isolation should not be considered a complete security sandbox.

Plugins are executable code and should therefore be treated as **trusted code** unless a future version explicitly introduces operating-system-level sandboxing.

Users should only install plugins from sources they trust.

### Logging and Sensitive Information

Logging must never expose sensitive information.

Logs must not contain:

- Passwords
- Authentication credentials
- Secrets
- Private keys
- Tokens
- Sensitive command arguments
- Other confidential values

When an operation requires logging identifying information for troubleshooting, only the minimum necessary information should be recorded.

Error messages presented to users should also avoid exposing sensitive system information unnecessarily.

### Package Manager Commands

Domain modules must not call package managers directly.

Package-manager operations must go through the appropriate adapter interface.

This provides a consistent boundary for:

- Command construction
- Argument handling
- Error handling
- Distribution-specific behavior
- Security review
- Testing

For example:

```text
Domain
  │
  ▼
PackageManagerAdapter
  │
  ▼
apt / dnf / pacman
```

This prevents individual domain implementations from creating their own unsafe package-manager invocation logic.

---

## Security Boundaries

The primary security-sensitive boundaries in Kommand are:

```text
┌──────────────────────────────────────┐
│              User Input              │
└──────────────────┬───────────────────┘
                   │
                   ▼
        ┌─────────────────────┐
        │ Validation / Domain │
        │      Logic          │
        └──────────┬──────────┘
                   │
                   ▼
        ┌─────────────────────┐
        │ Adapter / Core      │
        │ Infrastructure      │
        └──────────┬──────────┘
                   │
          ┌────────┴─────────┐
          │                  │
          ▼                  ▼
     System Commands      Privilege
                          Manager
          │                  │
          └────────┬─────────┘
                   ▼
             Operating System
```

Particular care is required whenever data crosses from an untrusted or user-controlled boundary into:

- Shell or subprocess execution
- Filesystem operations
- Privileged operations
- Package-manager commands
- Configuration loading
- Plugin execution

---

## Security Requirements for Contributors

Contributors should follow these rules when modifying Kommand:

1. Never log passwords, tokens, secrets, or credentials.
2. Never store sudo passwords or other credentials in configuration files.
3. Do not use `shell=True` for subprocess execution.
4. Use argument lists for subprocess commands.
5. Validate user-controlled input before using it in system operations.
6. Do not call package managers directly from domain modules.
7. Use the existing privilege-management infrastructure for privileged operations.
8. Keep privileged operations as narrow as possible.
9. Do not introduce unnecessary outbound network communication.
10. Add or update tests for security-sensitive behavior.
11. Document security implications for new features that cross a security boundary.
12. Treat third-party plugins as executable code and do not assume they are trusted merely because Kommand can load them.

---

## Reporting Security-Relevant Changes

Security-sensitive changes should be clearly identified during code review.

Examples include changes involving:

- `subprocess` execution
- Privilege escalation
- File permissions
- Authentication or authorization
- Credential handling
- Plugin loading
- Configuration loading
- Network communication
- Package-manager commands
- System service management
- User and group management

Pull requests containing such changes should explain:

- What security boundary is affected
- What input is considered untrusted
- How the input is validated
- Whether elevated privileges are required
- What sensitive information could be exposed
- How the behavior is tested

---

## Security Updates

Security fixes will be documented through the project's normal release and changelog process when disclosure is appropriate.

Security-sensitive releases may include:

- A patched version
- A description of the affected component
- The severity and impact
- Upgrade instructions
- Any required configuration changes

Users should keep Kommand updated and review release notes for security-related changes.

---

## Scope

This policy applies to the Kommand core application, official bundled plugins, package-manager adapters, CLI/TUI interfaces, and supporting repository infrastructure.

Third-party plugins and external software dependencies may have their own security policies and vulnerabilities. Their security posture is not automatically guaranteed by this policy.

---

## Disclaimer

Kommand is a system-management tool capable of performing operations that may modify the host operating system.

Users should review commands and operations before granting elevated privileges and should only install plugins and extensions from sources they trust.

No software can guarantee complete security. This policy describes Kommand's intended security controls and development practices; it does not guarantee that the software is free from vulnerabilities.
