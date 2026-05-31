# Extension surfaces — source-grounded detail

All citations are against the locally-installed package at
`~/.hermes/hermes-agent/`. Re-verify with `search_files` before relying on a
signature — line numbers drift between versions.

## 1. Plugin discovery and the override rule

`hermes_cli/plugins.py` module docstring (lines ~5-20) lists four sources, in
increasing priority:

1. Bundled — `<repo>/plugins/<name>/` (shipped by Nous)
2. User — `~/.hermes/plugins/<name>/`
3. Project — `./.hermes/plugins/<name>/` (opt-in via
   `HERMES_ENABLE_PROJECT_PLUGINS`)
4. Pip — packages exposing the `hermes_agent.plugins` entry-point group

Override rule (verbatim from the docstring): "Later sources override earlier
ones on name collision, so a user or project plugin with the same name as a
bundled plugin replaces it."

Each directory plugin needs a `plugin.yaml` manifest AND an `__init__.py` with
a `register(ctx)` function.

`get_bundled_plugins_dir()` honors `HERMES_BUNDLED_PLUGINS` (set by the Nix
wrapper) before falling back to the in-repo path — this is how read-only store
installs relocate the bundled dir without a fork.

## 2. Opt-in gating

`_get_enabled_plugins()` reads `plugins.enabled` from `config.yaml`. A plugin
loads only if its registry key is in that allow-list. `_get_disabled_plugins()`
reads `plugins.disabled` as an explicit deny-list that always wins. Use
`hermes plugins enable <name>` / `hermes plugins disable <name>` — do not edit
the protected `config.yaml` by hand.

## 3. VALID_HOOKS (the lifecycle hook names)

From `hermes_cli/plugins.py` `VALID_HOOKS` set:

- `pre_tool_call`, `post_tool_call`
- `transform_terminal_output`, `transform_tool_result`
- `transform_llm_output` (return a string to replace response text; first
  non-None wins)
- `pre_llm_call`, `post_llm_call`
- `pre_api_request`, `post_api_request`
- `on_session_start`, `on_session_end`, `on_session_finalize`,
  `on_session_reset`
- `subagent_stop`
- `pre_gateway_dispatch` (return `{"action": "skip|rewrite|allow", ...}`)
- `pre_approval_request`, `post_approval_response` (observers only; cannot veto)

The core fires these via `invoke_hook(name, **kwargs)`. `register_hook` raises
if `hook_name not in VALID_HOOKS`.

Hook return-value contract notes (verify in the live hook call site):
`pre_llm_call` returns `{"context": text}` to inject context — NOT
`{"messages": ...}`.

## 4. register_* signatures

From `hermes_cli/plugins.py` `PluginContext`:

- `register_command(name, handler, description="", args_hint="")` — handler
  signature is `fn(raw_args: str) -> str | None` (sync or async). Built-in
  collisions: it calls `resolve_command(clean)` from `hermes_cli.commands` and,
  if that resolves, logs "conflicts with a built-in command. Skipping." and
  returns. This is why `/model`, `/help`, etc. cannot be overridden.
- `register_cli_command(name, help, setup_fn, handler_fn=None, description="")`
  — `setup_fn(subparser)` adds argparse args; `handler_fn(args)` is the
  dispatch. Stored in `_cli_commands`; `main.py` builds a subparser per entry
  and dispatches via `args.func(args)`.
- `register_tool(...)` — delegates to `tools.registry.register()`.
- `register_context_engine(engine)` — must be an
  `agent.context_engine.ContextEngine`; only one allowed; REPLACES the built-in
  `ContextCompressor`.
- `register_image_gen_provider(provider)` / `register_dashboard_auth_provider(provider)`
  — type-checked; misbehaving providers are logged and ignored, never raised.

## 5. Built-in command behavior change (the /model example)

Because built-in commands are not overridable, you change their behavior via
their INPUTS. For `/model` specifically (handler in `cli.py`,
`_handle_model_command`): the picker is built from
`hermes_cli.inventory.build_models_payload` →
`hermes_cli.model_switch.list_authenticated_providers` →
`hermes_cli.models.cached_provider_model_ids`, which reads the disk cache at
`$HERMES_HOME/provider_models_cache.json` (TTL 3600s, credential-fingerprinted).
Levers: fewer authenticated providers in config, a warm cache, and the curated
catalog (do NOT call `provider_model_ids()` per row — it bypasses curation).

## 6. CLI command discovery cost

`main.py` `_plugin_cli_discovery_needed()` skips plugin discovery entirely when
the first positional arg is a known built-in subcommand, saving ~500-650ms.
An unknown token (your new `hermes <name>`) triggers discovery so the subparser
is built.

## 7. Manifest schema

`PluginManifest` dataclass fields: `name` (required, equals key), `version`,
`description`, `author`, `requires_env`, `provides_tools`, `provides_hooks`,
`source`, `path`, `kind` (`standalone` default | `backend` | `exclusive` |
`platform`), `key`. Bundled `backend` and `platform` plugins auto-load; user
plugins of any kind are still gated by `plugins.enabled`.
