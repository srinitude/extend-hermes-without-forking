# Contributing to extend-hermes-without-forking

Thanks for your interest in improving this skill. This project follows the
[building-deterministic-skills](https://agentskills.io) methodology: every
change must keep the skill easy for weak models to execute and must pass the
validators.

## Ground rules

1. **Keep it source-grounded.** Claims about Hermes internals (`VALID_HOOKS`,
   `register_*` signatures, the override rule) must match the live
   `~/.hermes/hermes-agent/` source. Cite file paths in
   `references/extension-surfaces.md`. Do not invent API shapes.
2. **Keep critical rules front-loaded and book-ended.** `## CRITICAL RULES` and
   `## Gotchas` stay near the top of `SKILL.md`; the final self-check repeats
   the load-bearing ones.
3. **Defaults, not menus.** The workflow has one default path. Put exceptions
   in `## Gotchas`.
4. **Offload exact checks to scripts.** Counting, hashing, frontmatter, and
   plugin-shape checks live in `scripts/`, each with a `--self-test` flag.
5. **No secrets, no network calls in scripts.** Validators are stdlib-only and
   offline (so they pass the Hermes security scan and run in clean CI).

## Local validation

Run the full pipeline before opening a PR:

```bash
python3 scripts/check-skill-frontmatter.py
python3 scripts/check-dumb-model-readability.py SKILL.md
python3 scripts/check-no-dead-links.py
python3 scripts/check-determinism.py
python3 scripts/validate-hermes-plugin.py assets/plugin-skeleton
```

If you have a local Hermes install, also confirm the security scan stays clean:
the skill must produce a `safe` or `caution` verdict (never `dangerous`) under
`tools.skills_guard.scan_skill(source="agent-created")`.

## Pull request checklist

- [ ] CI (`.github/workflows/ci.yml`) is green.
- [ ] `SKILL.md` body stays at or below 500 lines and 100000 chars.
- [ ] New reference files live under `references/`, `scripts/`, `assets/`, or
      `evals/` and are linked with an explicit load condition.
- [ ] New scripts support `--self-test` and are deterministic.
- [ ] Commit messages are descriptive; PRs explain the why, not just the what.

## Reporting issues

Use the issue templates. For anything security-sensitive, see
[SECURITY.md](SECURITY.md) instead of filing a public issue.

## License of contributions

By contributing, you agree that your contributions are licensed under the
[Apache License 2.0](LICENSE).
