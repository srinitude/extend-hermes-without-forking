"""plugin-skeleton — minimal valid Hermes user plugin.

Rename the directory and the ``name:`` in plugin.yaml to your plugin name,
then keep ONE of the register_* calls below and delete the rest.

A plugin does nothing until its directory name is added to ``plugins.enabled``
via ``hermes plugins enable <name>``. ``config.yaml`` is protected — use the
CLI, not a hand edit.
"""

from __future__ import annotations


# --- Option A: an in-session slash command (/<name>) ---------------------
# handler signature: fn(raw_args: str) -> str | None
def _handle_slash(raw_args: str) -> str:
    arg = (raw_args or "").strip()
    return f"plugin-skeleton slash command ran. args={arg!r}"


# --- Option B: a `hermes <name>` CLI subcommand --------------------------
def _setup(subparser) -> None:
    subparser.add_argument("--name", default="world", help="who to greet")


def _handle_cli(args) -> int:
    print(f"hello, {getattr(args, 'name', 'world')}")
    return 0


# --- Option C: a lifecycle hook ------------------------------------------
# Valid hook names are in hermes_cli.plugins.VALID_HOOKS. pre_llm_call returns
# {"context": text} to inject context (NOT {"messages": ...}).
def _on_session_start(**kwargs) -> None:
    # Observe-only example. Keep side effects cheap and fail-safe.
    return None


def register(ctx) -> None:
    # Keep at least one register_* call. Delete the options you do not use.
    ctx.register_command(
        "plugin-skeleton",
        handler=_handle_slash,
        description="Skeleton slash command — rename me.",
    )
    ctx.register_cli_command(
        name="plugin-skeleton",
        help="Skeleton CLI subcommand — rename me",
        setup_fn=_setup,
        handler_fn=_handle_cli,
        description="Rename this plugin and command before shipping.",
    )
    ctx.register_hook("on_session_start", _on_session_start)
