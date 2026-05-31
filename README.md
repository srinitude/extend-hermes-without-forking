# extend-hermes-without-forking

A deterministic [Agent Skill](https://agentskills.io) that teaches an AI agent
how to extend or override **Hermes** runtime behavior using the supported
plugin, config, skill, and environment layers in `~/.hermes/` — **never** by
editing the Nous-deployed package.

It is also a worked reference for the Hermes extension model: drop a same-named
plugin in `~/.hermes/plugins/` to override a bundled one, register hooks, tools,
slash commands, and CLI subcommands via `register(ctx)`, and change built-in
command behavior through inputs (config, caches, env) rather than by forking.

## Why

Editing `~/.hermes/hermes-agent/` to change behavior is lost on every upgrade.
Hermes is built so all customization layers on top of a pristine package. This
skill encodes that model as numbered, source-grounded procedures a weak model
can follow without guessing, plus validators that prove a plugin is well-formed.

## What's in the box

| Path | Purpose |
|------|---------|
| `SKILL.md` | The skill: critical rules, the five extension surfaces, the `PluginContext` API, an ordered workflow, output template, and verification checklist. |
| `references/extension-surfaces.md` | Source-grounded detail — `VALID_HOOKS`, `register_*` signatures, the override rule, the built-in-command-via-inputs pattern. |
| `assets/plugin-skeleton/` | A minimal valid Hermes user plugin (`plugin.yaml` + `register(ctx)`) to copy from. |
| `scripts/` | Deterministic validators (frontmatter, readability, dead links, determinism, plugin shape). Each supports `--self-test`. |
| `evals/evals.json` | Trigger, anti-trigger, and functional eval cases. |

## Install (Hermes)

```bash
hermes skills install srinitude/extend-hermes-without-forking --yes
```

Or pin a single file:

```bash
hermes skills install \
  https://raw.githubusercontent.com/srinitude/extend-hermes-without-forking/main/SKILL.md \
  --yes --name extend-hermes-without-forking
```

Verify:

```bash
hermes skills list --source hub
```

## Quick start: add your first plugin

```bash
cp -r assets/plugin-skeleton ~/.hermes/plugins/my-plugin
# edit plugin.yaml `name:` and __init__.py register(ctx) to match `my-plugin`
python3 scripts/validate-hermes-plugin.py ~/.hermes/plugins/my-plugin
hermes plugins enable my-plugin
hermes plugins list   # confirms my-plugin is enabled
```

## Validate locally

The validators are pure Python (stdlib only) and run on any Python 3.9+:

```bash
python3 scripts/check-skill-frontmatter.py
python3 scripts/check-dumb-model-readability.py SKILL.md
python3 scripts/check-no-dead-links.py
python3 scripts/check-determinism.py
python3 scripts/validate-hermes-plugin.py assets/plugin-skeleton
```

`check-skill-frontmatter.py` prefers the live Hermes validators when Hermes is
installed and falls back to an equivalent standalone check in clean CI.

## Contributing

Contributions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) and the
[Code of Conduct](CODE_OF_CONDUCT.md). All checks in
[`.github/workflows/ci.yml`](.github/workflows/ci.yml) must pass.

## License

[Apache License 2.0](LICENSE). See [NOTICE](NOTICE).
