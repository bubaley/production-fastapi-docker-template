import os
import re

import pytest
from conftest import ROOT

yaml = pytest.importorskip('yaml')

SKILLS = ROOT / '.agents' / 'skills'
CLAUDE_SKILLS = ROOT / '.claude' / 'skills'
NAME = re.compile(r'^[a-z0-9]+(-[a-z0-9]+)*$')
# Agent Skills spec fields; anything else is tool-specific and may break the other agent.
ALLOWED_FIELDS = {'name', 'description', 'license', 'compatibility', 'metadata', 'allowed-tools'}
LINK = re.compile(r'\]\(([^)#\s]+)(?:#[^)]*)?\)')


def _skill_dirs():
    return sorted(p for p in SKILLS.iterdir() if p.is_dir())


def _frontmatter(path):
    text = path.read_text()
    assert text.startswith('---\n'), f'{path}: frontmatter must open on the first line'
    block, _, body = text[4:].partition('\n---\n')
    return yaml.safe_load(block), body


def test_skills_exist():
    assert _skill_dirs(), 'no skills under .agents/skills'


@pytest.mark.parametrize('skill', _skill_dirs(), ids=lambda p: p.name)
def test_frontmatter_follows_agent_skills_spec(skill):
    meta, body = _frontmatter(skill / 'SKILL.md')
    assert isinstance(meta, dict)
    assert set(meta) <= ALLOWED_FIELDS, f'tool-specific fields: {set(meta) - ALLOWED_FIELDS}'
    assert meta.get('name') == skill.name
    assert NAME.match(meta['name']) and len(meta['name']) <= 64
    description = meta.get('description')
    assert isinstance(description, str) and 0 < len(description) <= 1024
    assert body.strip()


@pytest.mark.parametrize('skill', _skill_dirs(), ids=lambda p: p.name)
def test_relative_links_resolve(skill):
    _, body = _frontmatter(skill / 'SKILL.md')
    for target in LINK.findall(body):
        if '://' in target:
            continue
        assert (skill / target).exists(), f'{skill.name}: broken link {target}'


@pytest.mark.parametrize('skill', _skill_dirs(), ids=lambda p: p.name)
def test_claude_code_sees_skill_through_relative_symlink(skill):
    link = CLAUDE_SKILLS / skill.name
    assert link.is_symlink(), f'missing symlink: ln -s ../../.agents/skills/{skill.name} .claude/skills/{skill.name}'
    assert os.readlink(link) == f'../../.agents/skills/{skill.name}'
    assert (link / 'SKILL.md').is_file()


def test_no_claude_only_skills():
    for entry in CLAUDE_SKILLS.iterdir():
        assert entry.is_symlink(), f'{entry}: put the skill in .agents/skills/ and symlink it'
        assert entry.resolve().parent == SKILLS.resolve(), f'{entry}: dangling or foreign symlink'
