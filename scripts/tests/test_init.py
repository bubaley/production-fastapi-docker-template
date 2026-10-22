import json
import shutil
import subprocess

import pytest
from conftest import ROOT, load_script

init_script = load_script('scripts/bootstrap/init.py')

# Every file `make init` reads or rewrites.
SURFACE = (
    '.env.example',
    '.github/workflows/ci.yaml',
    '.template-version',
    'CHANGELOG.md',
    'Dockerfile',
    'Makefile',
    'README.md',
    'backend/app/main.py',
    'backend/pyproject.toml',
    'backend/uv.lock',
    'compose.yaml',
    'docs/deployment.md',
    'docs/product.md',
    'frontend/app/app.config.ts',
    'frontend/openapi.json',
    'frontend/package.json',
    'version.json',
)


def _git(repo, *args):
    return subprocess.run(
        ['git', '-c', 'user.name=Test', '-c', 'user.email=test@example.test', *args],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


@pytest.fixture
def repo(tmp_path):
    """A committed copy of the template's init surface."""
    for relative in (*SURFACE, '.gitignore'):
        target = tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(ROOT / relative, target)
    _git(tmp_path, 'init', '-q')
    _git(tmp_path, 'add', '-A')
    _git(tmp_path, 'commit', '-q', '-m', 'template')
    return tmp_path


def _env(repo):
    return init_script.env_values((repo / '.env').read_text())


def test_first_run_renames_resets_and_writes_env(repo):
    template_version = json.loads((repo / 'version.json').read_text())['version']
    head = _git(repo, 'rev-parse', 'HEAD')

    result = init_script.init(repo, 'field-service', 'Выездной сервис')

    assert result.warnings == []
    assert set(result.changed) == {*SURFACE, '.env'}
    read = lambda relative: (repo / relative).read_text()
    assert 'COMPOSE_PROJECT_NAME=field-service\n' in read('.env.example')
    assert 'SQL_DATABASE=field-service-db\n' in read('.env.example')
    assert 'name = "field-service"\nversion = "0.1.0"\n' in read('backend/pyproject.toml')
    assert '[[package]]\nname = "field-service"\nversion = "0.1.0"\nsource = { virtual = "." }' in read(
        'backend/uv.lock'
    )
    package = json.loads(read('frontend/package.json'))
    assert list(package)[:2] == ['name', 'version']
    assert package['name'] == 'field-service' and package['version'] == '0.1.0'
    assert "title='field-service'," in read('backend/app/main.py')
    assert json.loads(read('frontend/openapi.json'))['info']['title'] == 'field-service'
    assert "name: 'Выездной сервис'," in read('frontend/app/app.config.ts')
    assert read('README.md').startswith('# Выездной сервис\n')
    assert 'IMAGE ?= field-service:local' in read('Makefile')
    assert 'COMPOSE_PROJECT_NAME),field-service)-smoke' in read('Makefile')
    assert '${APP_IMAGE:-field-service:local}' in read('compose.yaml')
    assert 'CI_IMAGE: field-service:ci' in read('.github/workflows/ci.yaml')
    assert 'org.opencontainers.image.title="field-service"' in read('Dockerfile')
    assert '| `IMAGE_NAME` | publish | `field-service` |' in read('docs/deployment.md')
    assert 'fastapi-nuxt-template' not in read('docs/deployment.md') + read('README.md') + read('Makefile')
    assert json.loads(read('version.json')) == {'version': '0.1.0'}
    assert read('CHANGELOG.md') == init_script.CHANGELOG
    product = read('docs/product.md')
    assert product.startswith('# Выездной сервис\n')
    for heading in ('## Purpose', '## Personas', '## Scenarios', '## Non-goals'):
        assert heading in product
    recorded = init_script.read_template_version(repo)
    assert recorded['commit'] == head
    assert recorded['version'] == template_version
    assert recorded['repository'].startswith('https://')

    env = _env(repo)
    assert len(env['SECRET_KEY']) >= 64
    assert len(env['ENCRYPTION_KEY']) == 32
    assert env['COMPOSE_PROJECT_NAME'] == 'field-service'
    assert env['SECRET_KEY'] != init_script.env_values(read('.env.example'))['SECRET_KEY']


def test_second_run_changes_nothing(repo):
    init_script.init(repo, 'field-service', 'Выездной сервис')
    _git(repo, 'add', '-A')
    _git(repo, 'commit', '-q', '-m', 'init')
    env = (repo / '.env').read_text()

    result = init_script.init(repo, 'field-service', 'Выездной сервис')

    assert result.changed == []
    assert _git(repo, 'status', '--porcelain') == ''
    assert (repo / '.env').read_text() == env


def test_rename_after_init_keeps_versions_and_template_record(repo):
    init_script.init(repo, 'field-service', 'Выездной сервис')
    (repo / 'version.json').write_text('{\n  "version": "0.4.0"\n}\n')
    _git(repo, 'add', '-A')
    _git(repo, 'commit', '-q', '-m', 'release')
    recorded = init_script.read_template_version(repo)

    result = init_script.init(repo, 'service-desk', 'Сервис')

    assert result.warnings == []
    assert json.loads((repo / 'version.json').read_text()) == {'version': '0.4.0'}
    assert init_script.read_template_version(repo) == recorded
    assert 'name = "service-desk"' in (repo / 'backend/pyproject.toml').read_text()
    assert 'IMAGE ?= service-desk:local' in (repo / 'Makefile').read_text()


def test_refuses_a_dirty_tree_unless_forced(repo):
    (repo / 'README.md').write_text('local edit\n')

    with pytest.raises(init_script.InitError, match='uncommitted changes'):
        init_script.init(repo, 'field-service', 'Выездной сервис')
    assert not (repo / '.env').exists()

    init_script.init(repo, 'field-service', 'Выездной сервис', force=True)
    assert (repo / '.env').exists()


def test_existing_env_keeps_real_secrets_and_replaces_placeholders(repo):
    example = (repo / '.env.example').read_text()
    (repo / '.env').write_text(example.replace('SECRET_KEY=please-change-me', 'SECRET_KEY=mine-please-change-me'))

    init_script.init(repo, 'field-service', 'Выездной сервис')

    env = _env(repo)
    assert env['SECRET_KEY'].startswith('mine-')
    assert len(env['ENCRYPTION_KEY']) == 32
    assert env['ENCRYPTION_KEY'] != init_script.env_values(example)['ENCRYPTION_KEY']


@pytest.mark.parametrize(
    ('name', 'title'),
    [('Field', 'x'), ('field_service', 'x'), ('-field', 'x'), ('field', "It's"), ('field', '')],
)
def test_rejects_invalid_input(repo, name, title):
    with pytest.raises(init_script.InitError, match='Invalid'):
        init_script.init(repo, name, title)
    assert _git(repo, 'status', '--porcelain') == ''


def test_cli(repo, capsys):
    assert init_script.main(['field-service', '--root', str(repo), '--template-commit', 'abc123']) == 0
    assert 'make install' in capsys.readouterr().out
    assert init_script.read_template_version(repo)['commit'] == 'abc123'
    assert "name: 'Field Service'," in (repo / 'frontend/app/app.config.ts').read_text()
