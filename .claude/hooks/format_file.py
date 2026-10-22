#!/usr/bin/env python3
"""
PostToolUse hook (Edit|Write|MultiEdit): format only the file that was just changed.

- backend/**/*.py  → `ruff format` + `ruff check --fix` (backend/.venv/bin/ruff, else `uv run ruff`)
- frontend/**      → `vp fmt <file>` (Oxfmt through Vite+) for script, style, markup and data files
- anything else    → no-op

Never fails the tool call: formatter problems come back to the agent as a note (exit 0).
Python 3.9+, stdlib only.
"""

import json
import os
import shutil
import subprocess  # nosec B404
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BACKEND = ROOT / 'backend'
FRONTEND = ROOT / 'frontend'
TIMEOUT_SECONDS = 20

FRONTEND_SUFFIXES = {'.ts', '.tsx', '.mts', '.js', '.mjs', '.cjs', '.vue', '.json', '.jsonc', '.css', '.md'}
# Generated or vendored: formatting them by hand fights the generator.
FRONTEND_SKIP = ('node_modules/', '.nuxt/', '.output/', '.data/', 'public/', 'openapi.json', 'pnpm-lock.yaml')
BACKEND_SKIP = ('.venv/', 'migrations/')


def _relative(path, base):
    try:
        return path.relative_to(base).as_posix()
    except ValueError:
        return None


def _run(args, cwd):
    try:
        result = subprocess.run(  # nosec B603
            args, cwd=str(cwd), capture_output=True, text=True, timeout=TIMEOUT_SECONDS, check=False
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        return '{}: {}'.format(' '.join(args[:2]), error)
    if result.returncode != 0:
        output = (result.stdout + result.stderr).strip()
        return '{} exited with {}:\n{}'.format(' '.join(args[:3]), result.returncode, output[-1500:])
    return None


def _ruff():
    local = BACKEND / '.venv' / 'bin' / 'ruff'
    if local.exists():
        return [str(local)]
    if shutil.which('uv'):
        return ['uv', 'run', '--project', str(BACKEND), 'ruff']
    return None


def format_backend(path):
    ruff = _ruff()
    if ruff is None:
        return ['ruff not found: run `make install-backend`']
    notes = [_run([*ruff, 'format', str(path)], BACKEND), _run([*ruff, 'check', '--fix', str(path)], BACKEND)]
    return [note for note in notes if note]


def format_frontend(path):
    vp = FRONTEND / 'node_modules' / '.bin' / 'vp'
    if not vp.exists():
        return ['vp not found: run `make install-frontend`']
    note = _run([str(vp), 'fmt', '--no-error-on-unmatched-pattern', str(path)], FRONTEND)
    return [note] if note else []


def notes_for(file_path):
    path = Path(file_path)
    if not path.is_absolute():
        path = Path(os.environ.get('CLAUDE_PROJECT_DIR') or ROOT) / path
    if not path.is_file():
        return []
    backend = _relative(path, BACKEND)
    if backend is not None:
        if path.suffix != '.py' or any(part in backend for part in BACKEND_SKIP):
            return []
        return format_backend(path)
    frontend = _relative(path, FRONTEND)
    if frontend is not None:
        if path.suffix not in FRONTEND_SUFFIXES or any(part in frontend for part in FRONTEND_SKIP):
            return []
        return format_frontend(path)
    return []


def main():
    try:
        payload = json.load(sys.stdin)
    except ValueError:
        return 0
    tool_input = payload.get('tool_input') or {}
    file_path = tool_input.get('file_path') or tool_input.get('path')
    if not file_path:
        return 0
    try:
        notes = notes_for(file_path)
    except Exception as error:  # a hook must never break the edit
        notes = [f'format hook error: {error}']
    if notes:
        context = 'Auto-format of {} reported problems (the edit itself was applied):\n{}'.format(
            file_path, '\n'.join(notes)
        )
        print(json.dumps({'hookSpecificOutput': {'hookEventName': 'PostToolUse', 'additionalContext': context}}))
    return 0


if __name__ == '__main__':
    sys.exit(main())
