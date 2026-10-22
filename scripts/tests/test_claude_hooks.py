import json
import subprocess
import sys
import uuid

import pytest
from conftest import ROOT

HOOKS = ROOT / '.claude' / 'hooks'


def _run(hook, payload):
    return subprocess.run(
        [sys.executable, str(HOOKS / hook)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )


def _bash(command):
    return _run('block_migrations.py', {'tool_name': 'Bash', 'tool_input': {'command': command}})


@pytest.mark.parametrize(
    'command',
    [
        'make m',
        'make mm',
        'make migrate',
        'make make-migrations',
        'make lint && make m',
        'cd backend && python -m tortoise migrate',
        'cd backend && uv run tortoise makemigrations',
        'make -C .. -j2 migrate',
        'docker compose exec app python -m tortoise migrate',
        'bash -c "make mm"',
        'FOO=1 make m',
        'make lint\nmake m',
        "cat > x <<'EOF'\ntext\nEOF\nmake mm",
    ],
)
def test_migration_commands_are_blocked(command):
    result = _bash(command)
    assert result.returncode == 2
    assert 'ALLOW_MIGRATIONS=1' in result.stderr
    assert 'ask' in result.stderr


@pytest.mark.parametrize(
    'command',
    [
        'ALLOW_MIGRATIONS=1 make m',
        'cd backend && ALLOW_MIGRATIONS=1 python -m tortoise migrate',
        'env ALLOW_MIGRATIONS=1 make mm',
        'make lint',
        'make check PYTEST_ARGS=--sqlite',
        'make gen-client',
        'grep -rn "make m" docs',
        'echo tortoise migrate',
        'git commit -m "make m works"',
        'cd backend && uv run manage.py test --keepdb',
        'ls migrations',
        "cat > README.md <<'EOF'\nmake m   # apply migrations\nEOF\nmake lint",
        'python3 - <<EOF\nprint("make mm")\nEOF',
        'git commit -m "docs: quick start\n\nmake m\n"',
    ],
)
def test_other_commands_pass(command):
    result = _bash(command)
    assert result.returncode == 0, result.stderr
    assert result.stderr == ''


def test_block_hook_ignores_other_tools_and_bad_input():
    assert _run('block_migrations.py', {'tool_name': 'Edit', 'tool_input': {'command': 'make m'}}).returncode == 0
    result = subprocess.run(
        [sys.executable, str(HOOKS / 'block_migrations.py')],
        input='not json',
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0


def _format(path):
    return _run('format_file.py', {'tool_name': 'Write', 'tool_input': {'file_path': str(path)}})


@pytest.fixture
def scratch_file():
    """A file inside the real checkout (the hook only formats backend/ and frontend/), removed afterwards."""
    created = []

    def make(relative_dir, suffix, content):
        path = ROOT / relative_dir / f'_hook_probe_{uuid.uuid4().hex}{suffix}'
        path.write_text(content)
        created.append(path)
        return path

    yield make
    for path in created:
        path.unlink(missing_ok=True)


@pytest.mark.skipif(not (ROOT / 'backend/.venv/bin/ruff').exists(), reason='backend not installed')
def test_backend_python_is_formatted(scratch_file):
    path = scratch_file('backend/app', '.py', 'import sys\nimport os\nx = {"a":1}\nprint(os, sys, x)\n')

    result = _format(path)

    assert result.returncode == 0
    assert result.stdout == ''
    assert path.read_text() == "import os\nimport sys\n\nx = {'a': 1}\nprint(os, sys, x)\n"


@pytest.mark.skipif(not (ROOT / 'backend/.venv/bin/ruff').exists(), reason='backend not installed')
def test_formatter_failure_is_a_note_not_an_error(scratch_file):
    path = scratch_file('backend/app', '.py', 'def broken(:\n')

    result = _format(path)

    assert result.returncode == 0
    context = json.loads(result.stdout)['hookSpecificOutput']['additionalContext']
    assert 'reported problems' in context
    assert path.read_text() == 'def broken(:\n'


@pytest.mark.skipif(not (ROOT / 'frontend/node_modules/.bin/vp').exists(), reason='frontend not installed')
def test_frontend_file_is_formatted(scratch_file):
    path = scratch_file('frontend/app', '.ts', 'export const value = {a:1, "b": 2};\n')

    result = _format(path)

    assert result.returncode == 0, result.stdout
    assert path.read_text() == 'export const value = { a: 1, b: 2 }\n'


def test_paths_outside_backend_and_frontend_are_untouched(tmp_path, scratch_file):
    outside = tmp_path / 'x.py'
    outside.write_text('x = {"a":1}\n')
    docs = scratch_file('docs', '.md', '#  Title\n')
    migration = ROOT / 'backend/migrations' / '__init__.py'

    for path in (outside, docs, migration, ROOT / 'backend/app/does_not_exist.py'):
        result = _format(path)
        assert result.returncode == 0
        assert result.stdout == ''
    assert outside.read_text() == 'x = {"a":1}\n'
    assert docs.read_text() == '#  Title\n'


def test_settings_wire_both_hooks():
    settings = json.loads((ROOT / '.claude' / 'settings.json').read_text())
    pre = settings['hooks']['PreToolUse'][0]
    post = settings['hooks']['PostToolUse'][0]
    assert pre['matcher'] == 'Bash'
    assert 'block_migrations.py' in pre['hooks'][0]['command']
    assert set(post['matcher'].split('|')) >= {'Edit', 'Write'}
    assert 'format_file.py' in post['hooks'][0]['command']
