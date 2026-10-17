# Instructions for agents working with this repository

Read README.md first. This repository distributes the same `skills/` source to
Claude Code and Codex. Keep skills portable and keep provider-specific setup in
installation documentation.

When asked to install or update skills from this repository:

1. Identify the requested agent: `claude`, `codex`, or `both`. If the user only
   names the current agent, install for that agent. Install all groups unless
   the user selects specific ones.
2. Run `python3 scripts/install-skills.py --agent <agent> --dry-run`, then run
   the same command without `--dry-run`. Add `--group tasks obsidian` when
   appropriate. These commands copy real directories; they require Python 3.9+.
3. Preserve existing local changes. If preflight reports a conflict, explain
   the path and resolve it with the user; do not bypass the check or delete files.
4. Report installed skills, destination, and missing external dependencies.
   Todoist requires the `td` CLI and separate user authentication. Do not initiate
   authentication unless requested.

Use `.claude-plugin/marketplace.json` as the single source for skill groups.
Do not edit the generated upstream Todoist skill merely to change installation.
Do not install duplicate standalone Claude skills when the same skills are
already enabled through its marketplace plugin; choose one installation method.

For updates, pull the repository with `git pull --ff-only` and rerun the installer.
New groups and skills require rerunning installation. Removed skills are retained
locally; report them for manual review rather than deleting them automatically.
