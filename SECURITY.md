# Security Policy

## Reporting a vulnerability

If you discover a security issue in this skill — for example a validator that
could be bypassed, a plugin skeleton that encourages unsafe patterns, or
instructions that could lead an agent to leak secrets or modify the deployed
Hermes package — please **do not open a public issue**.

Instead, use GitHub's private vulnerability reporting:
**Security → Report a vulnerability** on this repository, or open a
[private security advisory](https://github.com/srinitude/extend-hermes-without-forking/security/advisories/new).

Please include:

- A description of the issue and its impact.
- Steps to reproduce (a minimal `SKILL.md`/plugin snippet is ideal).
- Any suggested remediation.

We aim to acknowledge reports within 7 days.

## Scope

This is a documentation-and-validators skill. The highest-impact concerns are:

1. Instructions that would cause an agent to edit the deployed package
   (`~/.hermes/hermes-agent/`) instead of layering in `~/.hermes/`.
2. Plugin examples that exfiltrate environment variables or credentials.
3. Validators that pass on a skill the Hermes security scanner would reject.

All shipped scripts are stdlib-only and perform no network or filesystem
writes outside the skill directory.
