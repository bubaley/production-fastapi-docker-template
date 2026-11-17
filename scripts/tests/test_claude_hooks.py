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


def test_settings_wire_the_format_hook():
    settings = json.loads((ROOT / '.claude' / 'settings.json').read_text())
    assert 'PreToolUse' not in settings['hooks']
    post = settings['hooks']['PostToolUse'][0]
    assert set(post['matcher'].split('|')) >= {'Edit', 'Write'}
    assert 'format_file.py' in post['hooks'][0]['command']
