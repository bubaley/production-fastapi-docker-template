"""
Turn a fresh copy of the template into a new product.

    make init name=my-product title="Мой продукт"
    python scripts/bootstrap/init.py my-product --title "Мой продукт" [--force] [--template-commit SHA]

- renames the project: COMPOSE_PROJECT_NAME / SQL_DATABASE / OTEL_SERVICE_NAME in .env.example, package names
  (backend/pyproject.toml + uv.lock, frontend/package.json), API title (main.py, openapi.json), product name
  (app.config.ts, README), image names (Makefile, compose.yaml, ci.yaml, Dockerfile, docs/deployment.md)
- writes .env from .env.example with a fresh SECRET_KEY and ENCRYPTION_KEY (an existing .env keeps its values;
  only the example placeholders are replaced)
- first run only: versions back to 0.1.0, empty CHANGELOG.md, docs/product.md reset to the product skeleton,
  .template-version records the template version and commit this product starts from

Idempotent: a second run with the same arguments changes nothing. Refuses a dirty git tree unless --force.
Standard library only.
"""

import argparse
import json
import re
import secrets
import subprocess  # nosec B404
import sys
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from string import Template

ROOT = Path(__file__).resolve().parents[2]
SKELETON = Path(__file__).resolve().parent / 'product.md.tmpl'
TEMPLATE_VERSION_FILE = '.template-version'
INITIAL_VERSION = '0.1.0'

NAME_PATTERN = re.compile(r'^[a-z][a-z0-9]*(-[a-z0-9]+)*$')
MAX_NAME_LENGTH = 40
TITLE_FORBIDDEN = re.compile(r'[\'"\\<>{}`\n]')

CHANGELOG = """# Changelog

All notable changes to this project are documented in this file.
It is generated from conventional commits by the release job; do not edit it by hand.
"""


class InitError(Exception):
    pass


@dataclass
class Result:
    changed: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def title_from_name(name: str) -> str:
    return ' '.join(part.capitalize() for part in name.split('-'))


def git(root: Path, *args: str) -> str:
    result = subprocess.run(['git', *args], cwd=root, capture_output=True, text=True, check=False)  # nosec B603 B607
    if result.returncode != 0:
        raise InitError(f'git {" ".join(args)} failed: {result.stderr.strip()}')
    return result.stdout.strip()


def read_template_version(root: Path) -> dict[str, str]:
    path = root / TEMPLATE_VERSION_FILE
    values: dict[str, str] = {}
    if path.exists():
        for line in path.read_text(encoding='utf-8').splitlines():
            if line.strip() and not line.lstrip().startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                values[key.strip()] = value.strip()
    return values


def write_template_version(root: Path, values: dict[str, str]) -> str:
    return (
        '# Template this product was created from; /sync-template diffs template-owned paths from `commit`\n'
        '# (or tag v<version> when the commit is not in the template history) and updates both.\n'
        '# See docs/template-ownership.md. Written by `make init`.\n'
        f'repository={values.get("repository", "")}\n'
        f'version={values.get("version", "")}\n'
        f'commit={values.get("commit", "")}\n'
    )


def current_slug(root: Path) -> str:
    match = re.search(
        r'^name = "([^"]+)"$', (root / 'backend/pyproject.toml').read_text(encoding='utf-8'), re.MULTILINE
    )
    if not match:
        raise InitError('backend/pyproject.toml has no `name = "..."` line')
    return match.group(1)


class Editor:
    """Collects file edits; nothing is written until `apply`, so a failed run leaves the tree untouched."""

    def __init__(self, root: Path, result: Result):
        self.root = root
        self.result = result
        self.pending: dict[str, str] = {}

    def read(self, relative: str) -> str | None:
        if relative in self.pending:
            return self.pending[relative]
        path = self.root / relative
        return path.read_text(encoding='utf-8') if path.exists() else None

    def write(self, relative: str, content: str) -> None:
        self.pending[relative] = content

    def sub(self, relative: str, pattern: str, replacement: str | Callable[[re.Match[str]], str], count: int = 0):
        """Regex replace; warns (template drift) when the pattern is missing."""
        source = self.read(relative)
        if source is None:
            self.result.warnings.append(f'{relative} not found; skipped')
            return
        updated, matches = re.subn(pattern, replacement, source, count=count, flags=re.MULTILINE)
        if not matches:
            self.result.warnings.append(f'{relative}: pattern {pattern!r} not found; update it by hand')
            return
        self.write(relative, updated)

    def apply(self) -> None:
        for relative, content in self.pending.items():
            path = self.root / relative
            if path.exists() and path.read_text(encoding='utf-8') == content:
                continue
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding='utf-8')
            self.result.changed.append(relative)


def rename(editor: Editor, old: str, new: str, title: str) -> None:
    image = re.escape(old)
    editor.sub('.env.example', r'^COMPOSE_PROJECT_NAME=.*$', f'COMPOSE_PROJECT_NAME={new}')
    editor.sub('.env.example', r'^SQL_DATABASE=.*$', f'SQL_DATABASE={new}-db')
    editor.sub('.env.example', r'^# OTEL_SERVICE_NAME=.*$', f'# OTEL_SERVICE_NAME={new}')
    editor.sub('backend/pyproject.toml', r'^name = "[^"]*"$', f'name = "{new}"', count=1)
    editor.sub('backend/uv.lock', rf'^(\[\[package\]\]\n)name = "{image}"$', rf'\1name = "{new}"', count=1)
    editor.sub('frontend/package.json', r'^  "name": "[^"]*",$', f'  "name": "{new}",', count=1)
    editor.sub('backend/app/main.py', r"^    title='[^']*',$", f"    title='{new}',", count=1)
    editor.sub('frontend/openapi.json', r'^    "title": "[^"]*",$', f'    "title": "{new}",', count=1)
    editor.sub('frontend/app/app.config.ts', r"^  name: '[^']*',$", f"  name: '{title}',", count=1)
    editor.sub('README.md', r'^# .*$', f'# {title}', count=1)
    editor.sub('Makefile', r'^IMAGE \?= .*$', f'IMAGE ?= {new}:local', count=1)
    editor.sub('Makefile', r'(COMPOSE_PROJECT_NAME\),)[^)]*(\)-smoke)', rf'\g<1>{new}\g<2>', count=1)
    editor.sub('compose.yaml', r'(\$\{APP_IMAGE:-)[^}]*(\})', rf'\g<1>{new}:local\g<2>', count=1)
    editor.sub('.github/workflows/ci.yaml', r'^(  CI_IMAGE: ).*$', rf'\g<1>{new}:ci', count=1)
    editor.sub('Dockerfile', r'(org\.opencontainers\.image\.title=")[^"]*(")', rf'\g<1>{new}\g<2>', count=1)
    editor.sub('docs/deployment.md', r'^(\| `IMAGE_NAME` \| publish \| `)[^`]*(` \|)$', rf'\g<1>{new}\g<2>', count=1)
    if old != new:
        for relative in ('docs/deployment.md', 'README.md'):
            source = editor.read(relative)
            if source is not None:
                editor.write(relative, re.sub(rf'(?<![\w.-]){image}:local\b', f'{new}:local', source))


def reset_versions(editor: Editor, old: str, new: str) -> None:
    editor.write('version.json', json.dumps({'version': INITIAL_VERSION}, indent=2) + '\n')
    editor.sub('backend/pyproject.toml', r'^version = "[^"]*"$', f'version = "{INITIAL_VERSION}"', count=1)
    editor.sub(
        'backend/uv.lock',
        rf'^(\[\[package\]\]\nname = "(?:{re.escape(old)}|{re.escape(new)})"\n)version = "[^"]*"$',
        rf'\g<1>version = "{INITIAL_VERSION}"',
        count=1,
    )
    package = editor.read('frontend/package.json') or ''
    if re.search(r'^  "version": ', package, re.MULTILINE):
        editor.sub('frontend/package.json', r'^  "version": "[^"]*",$', f'  "version": "{INITIAL_VERSION}",', count=1)
    else:
        # The release job keeps `version` right after `name` (Oxfmt's package.json order).
        editor.sub(
            'frontend/package.json', r'^(  "name": "[^"]*",)$', rf'\1\n  "version": "{INITIAL_VERSION}",', count=1
        )
    editor.write('CHANGELOG.md', CHANGELOG)


def env_values(source: str) -> dict[str, str]:
    values = {}
    for line in source.splitlines():
        if '=' in line and not line.lstrip().startswith('#'):
            key, value = line.split('=', 1)
            values[key.strip()] = value.strip()
    return values


def write_env(editor: Editor) -> None:
    """`.env` from `.env.example` with fresh secrets; an existing `.env` only loses the example placeholders."""
    example = editor.read('.env.example')
    if example is None:
        raise InitError('.env.example not found')
    placeholders = env_values(example)
    fresh = {'SECRET_KEY': secrets.token_urlsafe(64), 'ENCRYPTION_KEY': secrets.token_urlsafe(24)}
    assert len(fresh['SECRET_KEY']) >= 64 and len(fresh['ENCRYPTION_KEY']) == 32
    current = editor.read('.env')
    source = example if current is None else current
    for key, value in fresh.items():
        existing = env_values(source).get(key)
        if current is None or existing in (None, '', placeholders.get(key)):
            pattern = rf'^{key}=.*$'
            if re.search(pattern, source, re.MULTILINE):
                source = re.sub(pattern, f'{key}={value}', source, count=1, flags=re.MULTILINE)
            else:
                source = source.rstrip('\n') + f'\n{key}={value}\n'
    editor.write('.env', source)


def init(root: Path, name: str, title: str, *, force: bool = False, template_commit: str | None = None) -> Result:
    if not NAME_PATTERN.match(name) or len(name) > MAX_NAME_LENGTH:
        raise InitError(f'Invalid name {name!r}: kebab-case (a-z, 0-9, -), up to {MAX_NAME_LENGTH} characters')
    if not title.strip() or TITLE_FORBIDDEN.search(title):
        raise InitError(f'Invalid title {title!r}: plain text without quotes, backslashes, <>, {{}} or backticks')
    if git(root, 'rev-parse', '--is-inside-work-tree') != 'true':
        raise InitError(f'{root} is not a git work tree')
    if git(root, 'status', '--porcelain') and not force:
        raise InitError('The working tree has uncommitted changes; commit or stash them, or pass --force')

    result = Result()
    editor = Editor(root, result)
    old = current_slug(root)
    template = read_template_version(root)
    first_run = not template.get('commit')

    rename(editor, old, name, title)
    if first_run:
        version = json.loads(editor.read('version.json') or '{}').get('version', '')
        template_values = {
            'repository': template.get('repository', ''),
            'version': version,
            'commit': template_commit or git(root, 'rev-parse', 'HEAD'),
        }
        reset_versions(editor, old, name)
        skeleton = Template(SKELETON.read_text(encoding='utf-8')).substitute(title=title)
        editor.write('docs/product.md', skeleton)
        editor.write(TEMPLATE_VERSION_FILE, write_template_version(root, template_values))
    write_env(editor)
    editor.apply()

    if git(root, 'tag', '--list', 'v*'):
        result.warnings.append(
            'Template release tags (v*) are present; the release job would continue from them. '
            "Delete them before the first push: git tag --list 'v*' | xargs git tag -d"
        )
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('name', help='kebab-case product name, e.g. field-service')
    parser.add_argument('--title', help='product name shown in the UI, e.g. "Выездной сервис" (default: from name)')
    parser.add_argument('--force', action='store_true', help='run on a dirty working tree')
    parser.add_argument('--template-commit', help='template commit this copy starts from (default: HEAD)')
    parser.add_argument('--root', type=Path, default=ROOT, help=argparse.SUPPRESS)
    args = parser.parse_args(argv)

    try:
        result = init(
            args.root,
            args.name,
            args.title or title_from_name(args.name),
            force=args.force,
            template_commit=args.template_commit,
        )
    except InitError as e:
        print(f'init: {e}', file=sys.stderr)
        return 1

    if result.changed:
        print('Updated:\n' + '\n'.join(f'  {path}' for path in result.changed))
    else:
        print('Nothing to change: already initialized with these values.')
    for warning in result.warnings:
        print(f'Warning: {warning}', file=sys.stderr)
    print(
        '\nNext steps:\n'
        '  1. Review and commit: git add -A && git commit -m "chore: initialize from template"\n'
        '  2. make install\n'
        '  3. docker compose up -d db redis\n'
        '  4. make m                       # apply migrations (run it yourself; agents ask first)\n'
        '  5. make createsuperuser\n'
        '  6. make run-backend / make run-frontend (two terminals)\n'
        '  7. Describe the product in docs/product.md (purpose, personas, scenarios, non-goals)'
    )
    return 0


if __name__ == '__main__':
    sys.exit(main())
