<!-- Thanks for contributing! Please confirm the checklist below. -->

## What does this change?

<!-- Describe the change and the why, not just the what. -->

## Source grounding

<!-- If you changed claims about Hermes internals, cite the source path(s). -->

## Checklist

- [ ] I ran the full validator pipeline locally and it passed:
  - [ ] `python3 scripts/check-skill-frontmatter.py`
  - [ ] `python3 scripts/check-dumb-model-readability.py SKILL.md`
  - [ ] `python3 scripts/check-no-dead-links.py`
  - [ ] `python3 scripts/check-determinism.py`
  - [ ] `python3 scripts/validate-hermes-plugin.py assets/plugin-skeleton`
- [ ] Critical rules stayed front-loaded and book-ended in `SKILL.md`.
- [ ] New referenced files live under `references/`, `scripts/`, `assets/`, or `evals/`.
- [ ] New scripts support `--self-test` and are deterministic.
- [ ] I read [CONTRIBUTING.md](../CONTRIBUTING.md).
