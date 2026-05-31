---
name: extend-hermes-without-forking
description: >
  Extend or override Hermes runtime behavior using the supported plugin, config, skill, and env layers in ~/.hermes — never by editing the Nous-deployed package. Use when the user says "extend Hermes", "add a Hermes plugin", "override Hermes behavior", "add a slash command", "add a hermes CLI subcommand", "hook a tool call", "customize Hermes without forking", or "change Hermes without touching the package", even if they do not say "plugin" explicitly. Do NOT use for claude-code (Anthropic's claude CLI delegation), hermes-config-management (pure config.yaml audits), hermes-skill-operations (installing/updating skill packages), or hermes-tui-customization (TUI chrome) tasks.
license: Apache-2.0
version: 0.1.0
metadata:
  hermes:
    tags: [hermes, plugins, hooks, extension, runtime, customization]
    related_skills: [building-deterministic-skills, hermes-config-management, hermes-skill-operations, hermes-tui-customization]
---

# Extend Hermes without forking

Hermes is built so all customization lives OUTSIDE the deployed package, in
`~/.hermes/` and config. You override behavior by LAYERING, not by patching
files Nous ships. This skill names the five supported surfaces and gives one
default path for the most common job: adding a plugin that registers a hook,
tool, slash command, or CLI subcommand.

## CRITICAL RULES

1. NEVER edit files under the deployed package (`~/.hermes/hermes-agent/`). All
   changes go in `~/.hermes/plugins/`, `~/.hermes/skills/`, `config.yaml`, or
   environment variables. Package edits are lost on upgrade.
2. A user plugin at `~/.hermes/plugins/<name>/` with the SAME name as a bundled
   plugin REPLACES it. This is the override mechanism — use it, do not fork.
3. Built-in slash commands (`/model`, `/help`, `/cost`, etc.) CANNOT be
   overridden by a plugin. `register_command()` rejects any name that
   `resolve_command()` resolves. To change built-in behavior, influence its
   INPUTS (config, caches, env), not its handler.
4. Plugins are opt-in. A new user plugin does nothing until its directory name
   is in `plugins.enabled`. Enable with `hermes plugins enable <name>` — never
   hand-edit `config.yaml` (it is a protected file).
5. `config.yaml` is write-protected. Use `hermes plugins enable/disable` and
   `hermes config` commands; do not write the file directly.
6. Verify every claim against source before reporting. Use the exact commands
   in the Ordered workflow; do not rely on memory of the API shape.
7. Offload counting, frontmatter checks, and plugin-shape validation to the
   scripts in `scripts/`; do not eyeball them.
8. If a required fact is missing (target surface, plugin name, hook name),
   output `INSUFFICIENT CONTEXT: <field>` and stop instead of guessing.

## Gotchas

- Editing `~/.hermes/hermes-agent/` to change behavior: WRONG. Drop a
  same-named plugin in `~/.hermes/plugins/` instead.
- Expecting `register_command("model", ...)` to replace `/model`: it is
  silently skipped (built-in collision). Use a NEW command name, or change the
  built-in's inputs.
- Plugin written but "nothing happens": the directory name is not in
  `plugins.enabled`. Run `hermes plugins enable <name>` and start a new session.
- Hand-editing `config.yaml`: blocked as a protected file. Use the CLI.
- `register(ctx)` that registers nothing: a plugin must call at least one
  `ctx.register_*` method to have any effect.
- `pre_llm_call` returning `{"messages": ...}`: wrong shape. It returns
  `{"context": text}`. Read the live hook contract before writing one.
- Confusing the term "skill" (procedural markdown in `~/.hermes/skills/`) with
  "plugin" (executable code in `~/.hermes/plugins/`). One term per concept:
  PLUGIN = code, SKILL = procedure, CONFIG = `config.yaml`.

## The five extension surfaces

1. PLUGIN — executable Python in `~/.hermes/plugins/<name>/`
   (`plugin.yaml` + `__init__.py` with `register(ctx)`). Registers hooks,
   tools, slash commands, CLI subcommands, context engines, and backends.
2. CONFIG — the Hermes `config.yaml` (in `~/.hermes/`) selects providers,
   models, and which plugins load (`plugins.enabled` / `plugins.disabled`).
   Edited via the CLI.
3. SKILL — procedural markdown in `~/.hermes/skills/<name>/SKILL.md`. Overlays
   how a task is done; no executable override of the runtime. To author a new
   skill deterministically (so weak models can execute it) and validate it
   against Hermes, use the `building-deterministic-skills` skill — its
   methodology, skeleton, and validators. Repo:
   https://github.com/srinitude/building-deterministic-skills
   (install: `hermes skills install srinitude/building-deterministic-skills/. --yes`).
4. ENV VARS — flip behaviors at startup (e.g. `HERMES_BUNDLED_PLUGINS`,
   `HERMES_ENABLE_PROJECT_PLUGINS`, `HERMES_PLUGINS_DEBUG`).
5. ENTRY-POINT PIP PLUGIN — a pip package exposing the
   `hermes_agent.plugins` entry-point group; same `register(ctx)` contract.

Read `references/extension-surfaces.md` ONLY when you need the source-grounded
detail (file:line citations, full `VALID_HOOKS` list, `register_*` signatures,
hook return-value contracts).

## PluginContext API (the register surface)

A plugin's `register(ctx)` calls these. Read
`references/extension-surfaces.md` before using one you have not used before.

1. `ctx.register_hook(name, callback)` — run code at a lifecycle point. Valid
   names are in `VALID_HOOKS` (see reference).
2. `ctx.register_tool(...)` — add a model-callable tool.
3. `ctx.register_command(name, handler, description, args_hint)` — add an
   in-session slash command (`/<name>`). Built-in collisions are rejected.
4. `ctx.register_cli_command(name, help, setup_fn, handler_fn, description)` —
   add a `hermes <name>` terminal subcommand.
5. `ctx.register_context_engine(engine)` — replace the built-in compressor.
6. `ctx.register_image_gen_provider(...)` / `register_dashboard_auth_provider(...)`
   — pluggable backends.

## Ordered workflow

Default path: create one enabled user plugin in `~/.hermes/plugins/`, validate
it, and confirm it loads. Progress:

1. Confirm the target surface is a PLUGIN. If the user wants config-only
   edits, stop and defer to hermes-config-management; if skill packages, defer
   to hermes-skill-operations.
2. If the plugin name, target hook, or command name is missing, output
   `INSUFFICIENT CONTEXT: <field>` and stop.
3. Locate the package source root:
   `ls -d ~/.hermes/hermes-agent/hermes_cli/plugins.py`.
4. Read the live API you will use:
   `search_files` for `def register_command` / `def register_cli_command` /
   `VALID_HOOKS` in `~/.hermes/hermes-agent/hermes_cli/plugins.py`.
5. Pick the plugin directory name (lowercase, hyphens). This name is both the
   directory and the `plugins.enabled` key.
6. Copy the skeleton: `cp -r assets/plugin-skeleton ~/.hermes/plugins/<name>`
   then rename placeholders to `<name>` inside both files.
7. Write `plugin.yaml` with `name` equal to the directory name.
8. Write `__init__.py` with a `register(ctx)` that calls at least one
   `ctx.register_*` method.
9. For a slash command, confirm the name does NOT collide with a built-in:
   `search_files` for the name in `hermes_cli/commands.py` COMMAND_REGISTRY;
   if it resolves, choose a different name.
10. Validate the plugin shape:
    `python3 scripts/validate-hermes-plugin.py ~/.hermes/plugins/<name>`.
11. Enable it: `hermes plugins enable <name>`.
12. Confirm discovery: `hermes plugins list` shows `<name>` as `enabled`.
13. Exercise it: run the new `hermes <name>` subcommand, or trigger the hook,
    and capture real output. Do not report success without it.
14. Run the full Validation pipeline below and fix every failure before
    returning.

## Validation pipeline

1. **Frontmatter:** `python3 scripts/check-skill-frontmatter.py`
2. **Readability:** `python3 scripts/check-dumb-model-readability.py SKILL.md`
3. **No dead links:** `python3 scripts/check-no-dead-links.py`
4. **Determinism:** `python3 scripts/check-determinism.py`
5. **Plugin shape (functional):**
   `python3 scripts/validate-hermes-plugin.py assets/plugin-skeleton`
6. **Hermes security scan + discovery:** import
   `tools.skills_guard.scan_skill` with `source='agent-created'` and require
   `tools.skills_guard.should_allow_install(result)` returns `True`; import
   `agent.skill_utils.get_all_skills_dirs` and confirm the skill path is found.
7. **Hermes pytest gate:**
   `cd /Users/kiren/.hermes/hermes-agent && ./venv/bin/python -m pytest tests/tools/test_skill_manager_tool.py tests/tools/test_skill_size_limits.py tests/agent/test_skill_utils.py tests/tools/test_skills_guard.py -q`

## Output template

```text
Surface: PLUGIN | CONFIG | SKILL | ENTRYPOINT | ENV
Plugin name:
Registered: <hook|tool|command|cli_command|backend>
Enabled: <yes via `hermes plugins enable <name>` | n/a>
Evidence: <hermes plugins list line + real command output>
Validation: <each pipeline command + PASS/FAIL>
Package edited: NO
```

## INSUFFICIENT CONTEXT escape hatch

If any of these are unknown, emit `INSUFFICIENT CONTEXT: <field>` and stop:
the extension surface, the plugin directory name, the hook name (for a hook),
or the slash/CLI command name (for a command). Do not invent an API shape.

## Critical-rule placement note

These critical rules are intentionally front-loaded at the top of this file and
book-ended: the final self-check below repeats the load-bearing ones so a weak
model re-reads them before finishing.

## Verification checklist

- [ ] No file under `~/.hermes/hermes-agent/` was edited (package untouched).
- [ ] The plugin lives in `~/.hermes/plugins/<name>/` with `plugin.yaml` +
      `__init__.py` and a `register(ctx)` that calls a `ctx.register_*` method.
- [ ] No slash command name collides with a built-in (`resolve_command`).
- [ ] `hermes plugins enable <name>` was run and `hermes plugins list` shows it
      enabled.
- [ ] The new command/hook was exercised and real output was captured.
- [ ] `scripts/check-skill-frontmatter.py` passes.
- [ ] `scripts/check-dumb-model-readability.py SKILL.md` passes.
- [ ] `scripts/check-no-dead-links.py` passes.
- [ ] `scripts/check-determinism.py` passes.
- [ ] `scripts/validate-hermes-plugin.py assets/plugin-skeleton` passes.
- [ ] `tools.skills_guard.scan_skill(source='agent-created')` returns
      `allowed=True` via `should_allow_install`.
- [ ] The Hermes pytest gate passes.
- [ ] Critical rules stayed front-loaded and book-ended.
