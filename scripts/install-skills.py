#!/usr/bin/env python3
"""Copy this repository's skills into user-level Claude/Codex skill directories."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
MARKER = '.bruski-skills.json'


def hashes(folder):
    return {str(p.relative_to(folder)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(folder.rglob('*')) if p.is_file()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--agent', required=True, choices=['claude', 'codex', 'both'])
    parser.add_argument('--group', nargs='+', help='Marketplace groups; default: all')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    catalog = json.loads((ROOT / '.claude-plugin/marketplace.json').read_text())
    groups = {p['name']: p['skills'] for p in catalog['plugins']}
    selected = args.group or list(groups)
    unknown = set(selected) - groups.keys()
    if unknown:
        parser.error('Unknown groups: ' + ', '.join(sorted(unknown)))
    sources = sorted({(ROOT / s).resolve() for g in selected for s in groups[g]})
    for source in sources:
        if not source.is_relative_to(ROOT / 'skills') or not (source / 'SKILL.md').is_file():
            parser.error(f'Invalid skill source: {source}')
        if any(p.is_symlink() for p in source.rglob('*')):
            parser.error(f'Skill contains symlinks: {source}')
    targets = {'claude': Path.home() / '.claude/skills',
               'codex': Path.home() / '.agents/skills'}
    agents = list(targets) if args.agent == 'both' else [args.agent]
    plans = []
    # Preflight every destination before copying any skills.
    for agent in agents:
        target = targets[agent]
        marker = target / MARKER
        if marker.is_symlink():
            parser.error(f'Refusing symlink manifest: {marker}')
        manifest = json.loads(marker.read_text()) if marker.exists() else {}
        for source in sources:
            dest = target / source.name
            current = hashes(source)
            if dest.is_symlink():
                parser.error(f'Existing symlink; resolve it manually first: {dest}')
            if dest.exists():
                if not dest.is_dir():
                    parser.error(f'Destination is not a directory: {dest}')
                existing = hashes(dest)
                if existing != current and existing != manifest.get(source.name):
                    parser.error(f'Unmanaged or locally modified skill; preserve or move it first: {dest}')
            plans.append((source, dest, current))
        plans.append((None, marker, manifest))
    for source, dest, data in plans:
        if source is not None:
            print(f'{"Would copy" if args.dry_run else "Copy"}: {source.name} -> {dest}')
            if not args.dry_run:
                dest.parent.mkdir(parents=True, exist_ok=True)
                if dest.exists():
                    shutil.rmtree(dest)
                shutil.copytree(source, dest)
        elif not args.dry_run:
            for s in sources:
                data[s.name] = hashes(s)
            dest.write_text(json.dumps(data, indent=2) + '\n')
    print('Preview complete.' if args.dry_run else 'Installed. Skills are available on the next turn; restart the agent if needed.')


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError) as exc:
        print(f'Installation failed: {exc}', file=sys.stderr)
        sys.exit(1)
