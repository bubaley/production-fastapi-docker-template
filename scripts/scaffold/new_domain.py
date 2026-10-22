"""
Scaffold a backend domain + frontend feature that mirror the canonical `organization` code.

    make new-domain name=project title="Проекты" item_title="Проект"
    python scripts/scaffold/new_domain.py project --title "Проекты" [--item-title "Проект"] [--plural projects]

Creates an organization-scoped CRUD entity with a `name` field: backend models/schemas/filters/views/tests,
frontend resource descriptor, list/detail views, settings pages and a settings drawer entry. It never
overwrites a file and runs no migrations. Standard library only (string.Template).
"""

import argparse
import keyword
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from string import Template

ROOT = Path(__file__).resolve().parents[2]
TEMPLATES = Path(__file__).resolve().parent / 'templates'
NAVIGATION = Path('frontend/app/navigation/settings.ts')
NAVIGATION_MARKER = '  // new-domain: entries above this line\n'
DEFAULT_ICON = 'Folder'

NAME_PATTERN = re.compile(r'^[a-z][a-z0-9]*(_[a-z0-9]+)*$')
# Longer names push generated lines past the 120-column limit.
MAX_NAME_LENGTH = 24
LINE_LENGTH = 120
# Kernel domains and names that clash with framework modules or existing routes.
TITLE_FORBIDDEN = re.compile(r'[\'"\\<>{}`]')
RESERVED = {'auth', 'user', 'organization', 'core', 'shared', 'domains', 'settings', 'profile', 'models', 'test'}


class ScaffoldError(Exception):
    pass


def pluralize(word: str) -> str:
    if re.search(r'[^aeiou]y$', word):
        return word[:-1] + 'ies'
    if re.search(r'(s|x|z|ch|sh)$', word):
        return word + 'es'
    return word + 's'


def pascal(snake: str) -> str:
    return ''.join(part.capitalize() for part in snake.split('_'))


def camel(snake: str) -> str:
    value = pascal(snake)
    return value[0].lower() + value[1:]


def python_import(module: str, names: list[str]) -> str:
    line = f'from {module} import {", ".join(names)}'
    if len(line) <= LINE_LENGTH:
        return line
    body = ''.join(f'    {name},\n' for name in names)
    return f'from {module} import (\n{body})'


@dataclass(frozen=True)
class Names:
    name: str  # snake singular: invoice_line
    plural: str  # snake plural: invoice_lines
    title: str  # list title and drawer label (Russian)
    item_title: str  # detail title (Russian)

    @property
    def context(self) -> dict[str, str]:
        name_pascal = pascal(self.name)
        plural_kebab = self.plural.replace('_', '-')
        return {
            'name': self.name,
            'Name': name_pascal,
            'camel': camel(self.name),
            'plural': self.plural,
            'plural_kebab': plural_kebab,
            'sdkPrefix': camel(self.plural),
            'route': f'settings-{plural_kebab}',
            'title': self.title,
            'item_title': self.item_title,
            'schemas_import': python_import(
                f'app.domains.{self.name}.schemas',
                [f'{name_pascal}CreateSchema', f'{name_pascal}ReadSchema', f'{name_pascal}UpdateSchema'],
            ),
        }


def validate_title(title: str) -> None:
    if not title.strip() or TITLE_FORBIDDEN.search(title):
        raise ScaffoldError(f'Invalid title {title!r}: plain text without quotes, backslashes, <>, {{}} or backticks')


def validate(name: str, plural: str) -> None:
    if not NAME_PATTERN.match(name) or len(name) > MAX_NAME_LENGTH:
        raise ScaffoldError(
            f'Invalid name {name!r}: use singular snake_case (a-z, 0-9, _), up to {MAX_NAME_LENGTH} characters'
        )
    if not NAME_PATTERN.match(plural):
        raise ScaffoldError(f'Invalid plural {plural!r}: use snake_case')
    if plural == name:
        raise ScaffoldError(f'Plural {plural!r} equals the name; pass a different --plural')
    if name in RESERVED or keyword.iskeyword(name) or keyword.iskeyword(plural):
        raise ScaffoldError(f'Name {name!r} is reserved')


def plan(names: Names) -> list[tuple[str, Path]]:
    """(template, target path relative to the root) for every generated file."""
    ctx = names.context
    backend = Path('backend/app/domains') / names.name
    feature = Path('frontend/app/features') / ctx['camel']
    pages = Path('frontend/app/pages/settings') / ctx['plural_kebab']
    return [
        ('', backend / '__init__.py'),
        ('backend/models.py.tmpl', backend / 'models.py'),
        ('backend/schemas.py.tmpl', backend / 'schemas.py'),
        ('backend/filters.py.tmpl', backend / 'filters.py'),
        ('backend/views.py.tmpl', backend / 'views.py'),
        ('', backend / 'services' / '__init__.py'),
        ('', backend / 'tests' / '__init__.py'),
        ('backend/test.py.tmpl', backend / 'tests' / f'test_{names.name}.py'),
        ('frontend/resource.ts.tmpl', feature / 'resources' / f'{ctx["camel"]}.ts'),
        ('frontend/ListView.vue.tmpl', feature / 'views' / f'{ctx["Name"]}ListView.vue'),
        ('frontend/DetailView.vue.tmpl', feature / 'views' / f'{ctx["Name"]}DetailView.vue'),
        ('frontend/page.vue.tmpl', pages / 'index.vue'),
        ('frontend/page.vue.tmpl', pages / '[id].vue'),
    ]


def render(template: str, target: Path, ctx: dict[str, str]) -> str:
    if not template:
        return ''
    values = dict(ctx)
    if template == 'frontend/page.vue.tmpl':
        kind = 'Detail' if target.name == '[id].vue' else 'List'
        values['view'] = f'{ctx["Name"]}{kind}View'
    return Template((TEMPLATES / template).read_text(encoding='utf-8')).substitute(values)


def navigation_entry(ctx: dict[str, str], icon: str = DEFAULT_ICON) -> str:
    return f"  {{ to: {{ name: '{ctx['route']}' }}, label: '{ctx['title']}', icon: {icon} }},\n"


def add_navigation(source: str, ctx: dict[str, str], icon: str = DEFAULT_ICON) -> str:
    """Insert the drawer entry above the marker and add the icon to the `@lucide/vue` import."""
    if f"name: '{ctx['route']}'" in source:
        raise ScaffoldError(f'{NAVIGATION} already has an entry for {ctx["route"]}')
    if NAVIGATION_MARKER not in source:
        raise ScaffoldError(f'{NAVIGATION} has no marker line {NAVIGATION_MARKER.strip()!r}')
    source = source.replace(NAVIGATION_MARKER, navigation_entry(ctx, icon) + NAVIGATION_MARKER)
    match = re.search(r"^import \{ ([^}]*) \} from '@lucide/vue'$", source, flags=re.MULTILINE)
    if match is None:
        return f"import {{ {icon} }} from '@lucide/vue'\n" + source
    icons = sorted({part.strip() for part in match.group(1).split(',') if part.strip()} | {icon})
    return source.replace(match.group(0), f"import {{ {', '.join(icons)} }} from '@lucide/vue'")


def scaffold(names: Names, root: Path = ROOT) -> list[Path]:
    validate(names.name, names.plural)
    validate_title(names.title)
    validate_title(names.item_title)
    ctx = names.context
    files = plan(names)
    if (root / 'backend/app/domains' / names.name).exists():
        raise ScaffoldError(f'Domain backend/app/domains/{names.name} already exists')
    existing = [str(target) for _, target in files if (root / target).exists()]
    if existing:
        raise ScaffoldError('Refusing to overwrite existing files:\n  ' + '\n  '.join(existing))

    rendered = [(target, render(template, target, ctx)) for template, target in files]
    navigation = root / NAVIGATION
    nav_source = add_navigation(navigation.read_text(encoding='utf-8'), ctx) if navigation.exists() else None

    for target, content in rendered:
        path = root / target
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('x', encoding='utf-8') as handle:
            handle.write(content)
    written = [target for target, _ in rendered]
    if nav_source is not None:
        navigation.write_text(nav_source, encoding='utf-8')
        written.append(NAVIGATION)
    return written


def next_steps(names: Names, navigation_updated: bool) -> str:
    ctx = names.context
    navigation = (
        f'Navigation: entry added to {NAVIGATION} (icon {DEFAULT_ICON}; pick a fitting Lucide icon).'
        if navigation_updated
        else f'Navigation: add to the settings drawer:\n     {navigation_entry(ctx).strip()}'
    )
    steps = [
        (
            f'Fill the real fields: backend/app/domains/{names.name}/ models.py, schemas.py, filters.py, then '
            f'the frontend resource ({ctx["camel"]}.ts) and views.'
        ),
        (
            'Migration: the new table needs `make mm` then `make m`. Agents never run them: ask the user. '
            'Until then test with `--sqlite`.'
        ),
        '`make gen-client`: regenerates frontend/openapi.json and the typed client the resource imports.',
        f'`cd backend && uv run pytest app/domains/{names.name} --sqlite`, then `make lint` and `make check`.',
        navigation,
        'docs/product.md: describe what the user can now see or do (UI copy in Russian).',
    ]
    return '\n'.join(f'  {index}. {step}' for index, step in enumerate(steps, 1))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('name', help='singular snake_case name, e.g. project or invoice_line')
    parser.add_argument('--title', help='Russian list title and drawer label, e.g. "Проекты"')
    parser.add_argument('--item-title', help='Russian detail title, e.g. "Проект" (default: --title)')
    parser.add_argument('--plural', help='snake_case plural when the default (+s/+es/-y→ies) is wrong')
    parser.add_argument('--root', type=Path, default=ROOT, help=argparse.SUPPRESS)
    args = parser.parse_args(argv)

    title = args.title or pascal(args.name)
    names = Names(
        name=args.name,
        plural=args.plural or pluralize(args.name),
        title=title,
        item_title=args.item_title or title,
    )
    try:
        written = scaffold(names, args.root)
    except ScaffoldError as e:
        print(f'new-domain: {e}', file=sys.stderr)
        return 1

    print(f'Created {names.name} ({names.plural}, /api/v1/{names.context["plural_kebab"]}):')
    for path in written:
        print(f'  {path}')
    if not args.title:
        print(f'\nWarning: no title given; the UI says "{title}". Replace it with Russian copy.')
    print('\nNext steps:')
    print(next_steps(names, NAVIGATION in written))
    return 0


if __name__ == '__main__':
    sys.exit(main())
