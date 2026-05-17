# bruski-claude-plugins

Personal, private [Claude Code plugin marketplace](https://code.claude.com/docs/en/plugin-marketplaces) for syncing custom skills across devices.

## Install on a new device

```text
/plugin marketplace add bruceeewong/bruski-claude-plugins
/plugin install tasks@bruski-claude-plugins
```

You only install the plugins you need on a given device — selective install is the whole point.

## Update everywhere

```text
/plugin marketplace update bruski-claude-plugins
```

## Plugins

| Plugin     | Skills                                                                                       | Description                                          |
|------------|----------------------------------------------------------------------------------------------|------------------------------------------------------|
| `tasks`    | `task-create`, `task-read`, `task-update`, `task-list`, `task-complete`, `task-discard`     | Task documentation workflow (plan/todo/report/lesson) |
| `obsidian` | `manage-inbox-notes`                                                                         | Process and distribute Obsidian vault inbox notes into the knowledge base |

## Repo layout

```
.
├── .claude-plugin/
│   └── marketplace.json     # marketplace + plugin definitions
├── skills/                   # flat directory of all skills
│   └── <skill-name>/SKILL.md
├── README.md
└── .gitignore
```

## Adding a new themed plugin

1. Drop the new skill folder under `skills/<skill-name>/` with its `SKILL.md`.
2. Add a new entry to `plugins[]` in `.claude-plugin/marketplace.json`:
   ```json
   {
     "name": "<theme>",
     "description": "...",
     "source": "./",
     "strict": false,
     "skills": ["./skills/<skill-name>"]
   }
   ```
3. Commit, push.
4. On each device that wants it: `/plugin marketplace update bruski-claude-plugins` then `/plugin install <theme>@bruski-claude-plugins`.

No directory reshuffling — every plugin shares the flat `skills/` root. New themes just bundle existing skill folders by name.
