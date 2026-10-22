import py_compile
import shutil
import subprocess
import sys

import pytest
from conftest import ROOT, load_script

new_domain = load_script('scripts/scaffold/new_domain.py')

RUFF_CONFIG = ROOT / 'backend' / 'pyproject.toml'
# The generated domain lives outside backend/, so isort cannot infer that `app` is first-party.
FIRST_PARTY = "lint.isort.known-first-party = ['app']"


@pytest.fixture
def project_root(tmp_path):
    """An empty checkout with only the settings navigation registry."""
    navigation = tmp_path / new_domain.NAVIGATION
    navigation.parent.mkdir(parents=True)
    shutil.copy(ROOT / new_domain.NAVIGATION, navigation)
    return tmp_path


def _names(name, title='Счета', item_title='Счёт', plural=None):
    return new_domain.Names(name=name, plural=plural or new_domain.pluralize(name), title=title, item_title=item_title)


def _ruff(*args):
    return subprocess.run(
        [sys.executable, '-m', 'ruff', *args, '--config', str(RUFF_CONFIG), '--config', FIRST_PARTY],
        check=False,
        capture_output=True,
        text=True,
    )


@pytest.mark.parametrize('name', ['invoice', 'customer_address_history'])
def test_generates_the_canonical_files(project_root, name):
    names = _names(name)
    written = new_domain.scaffold(names, project_root)

    ctx = names.context
    backend = project_root / 'backend/app/domains' / name
    expected = {
        backend / '__init__.py',
        backend / 'models.py',
        backend / 'schemas.py',
        backend / 'filters.py',
        backend / 'views.py',
        backend / 'services/__init__.py',
        backend / 'tests/__init__.py',
        backend / f'tests/test_{name}.py',
        project_root / f'frontend/app/features/{ctx["camel"]}/resources/{ctx["camel"]}.ts',
        project_root / f'frontend/app/features/{ctx["camel"]}/views/{ctx["Name"]}ListView.vue',
        project_root / f'frontend/app/features/{ctx["camel"]}/views/{ctx["Name"]}DetailView.vue',
        project_root / f'frontend/app/pages/settings/{ctx["plural_kebab"]}/index.vue',
        project_root / f'frontend/app/pages/settings/{ctx["plural_kebab"]}/[id].vue',
        project_root / new_domain.NAVIGATION,
    }
    assert {project_root / path for path in written} == expected
    assert all(path.is_file() for path in expected)

    python_files = sorted(backend.rglob('*.py'))
    for path in python_files:
        py_compile.compile(str(path), doraise=True)
    lint = _ruff('check', *map(str, python_files))
    assert lint.returncode == 0, lint.stdout + lint.stderr
    fmt = _ruff('format', '--check', '--diff', *map(str, python_files))
    assert fmt.returncode == 0, fmt.stdout + fmt.stderr

    views = (backend / 'views.py').read_text()
    assert f'routers = ({ctx["plural"]}_router,)' in views
    assert f"tags=['{ctx['plural_kebab']}']" in views
    assert "user='organization__org_users__user_id'" in (backend / 'models.py').read_text()
    resource_source = (project_root / f'frontend/app/features/{ctx["camel"]}/resources/{ctx["camel"]}.ts').read_text()
    assert f'{ctx["sdkPrefix"]}List,' in resource_source
    assert f"key: '{ctx['plural_kebab']}'" in resource_source
    list_view = (project_root / f'frontend/app/features/{ctx["camel"]}/views/{ctx["Name"]}ListView.vue').read_text()
    assert 'title="Счета"' in list_view
    assert f'detail-route-name="settings-{ctx["plural_kebab"]}-id"' in list_view
    navigation = (project_root / new_domain.NAVIGATION).read_text()
    assert f"{{ to: {{ name: 'settings-{ctx['plural_kebab']}' }}, label: 'Счета', icon: Folder }}," in navigation
    assert "import { Building, Folder, User, Users } from '@lucide/vue'" in navigation
    assert navigation.index('settings-users') < navigation.index(f'settings-{ctx["plural_kebab"]}')


def test_refuses_to_overwrite(project_root):
    names = _names('invoice')
    page = project_root / 'frontend/app/pages/settings/invoices/index.vue'
    page.parent.mkdir(parents=True)
    page.write_text('mine')

    with pytest.raises(new_domain.ScaffoldError, match='Refusing to overwrite'):
        new_domain.scaffold(names, project_root)
    assert page.read_text() == 'mine'
    assert not (project_root / 'backend').exists()


def test_refuses_an_existing_domain(project_root):
    new_domain.scaffold(_names('invoice'), project_root)
    with pytest.raises(new_domain.ScaffoldError, match='already exists'):
        new_domain.scaffold(_names('invoice'), project_root)


@pytest.mark.parametrize('name', ['Invoice', 'invoice-line', '1invoice', 'invoice__line', 'user', 'class', 'a' * 25])
def test_rejects_invalid_names(project_root, name):
    with pytest.raises(new_domain.ScaffoldError):
        new_domain.scaffold(_names(name, plural='things'), project_root)


@pytest.mark.parametrize('title', ['', "Счёт's", 'Счета "x"', '<b>Счета</b>'])
def test_rejects_titles_that_break_the_generated_code(project_root, title):
    with pytest.raises(new_domain.ScaffoldError, match='Invalid title'):
        new_domain.scaffold(_names('invoice', title=title), project_root)


@pytest.mark.parametrize(
    ('word', 'plural'),
    [
        ('project', 'projects'),
        ('category', 'categories'),
        ('day', 'days'),
        ('box', 'boxes'),
        ('invoice_batch', 'invoice_batches'),
    ],
)
def test_pluralize(word, plural):
    assert new_domain.pluralize(word) == plural


def test_cli_prints_next_steps(project_root, capsys):
    code = new_domain.main(['invoice', '--title', 'Счета', '--root', str(project_root)])

    assert code == 0
    out = capsys.readouterr().out
    assert 'make gen-client' in out
    assert 'make mm' in out
    assert 'docs/product.md' in out
    assert new_domain.main(['invoice', '--root', str(project_root)]) == 1
