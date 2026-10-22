#!/usr/bin/env python3
"""
PreToolUse hook (Bash): block database migration commands.

Agents never create or apply migrations on their own (AGENTS.md). Blocked: `make m | mm | migrate |
make-migrations` and `tortoise migrate | makemigrations | upgrade | downgrade` in any form (`python -m`,
`uv run`, `docker compose exec`, `bash -c`). When the user explicitly asked for it, prefix the command with
`ALLOW_MIGRATIONS=1`, e.g. `ALLOW_MIGRATIONS=1 make m`.

Reads the hook JSON on stdin; exit 2 blocks the call and shows stderr to the agent. Python 3.9+, stdlib only.
"""

import json
import re
import shlex
import sys

MAKE_TARGETS = {'m', 'mm', 'migrate', 'make-migrations'}
TORTOISE_COMMANDS = {'migrate', 'makemigrations', 'upgrade', 'downgrade'}
MAKE_OPTIONS_WITH_VALUE = {'-C', '-f', '--file', '--makefile', '-I', '--include-dir', '-j', '--jobs', '-o', '-W'}
SHELLS = {'sh', 'bash', 'zsh', 'dash'}
# Commands that only print or search text: `echo tortoise migrate`, `grep -rn "make m"` are fine.
TEXT_COMMANDS = {'echo', 'printf', 'grep', 'rg', 'git', 'cat', 'sed', 'awk', 'less', 'head', 'tail'}
ASSIGNMENT = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*=')
HEREDOC = re.compile(r'<<-?\s*([\'"]?)([A-Za-z_][A-Za-z0-9_]*)\1')
SEPARATORS = '();<>|&\n'
ALLOW = 'ALLOW_MIGRATIONS=1'

MESSAGE = (
    'Blocked: `{command}` creates or applies database migrations. Agents do not run migrations on their own '
    '(AGENTS.md). Tell the user which migration is needed and ask them to run it. Only if the user explicitly '
    'asked you to run it, retry with the prefix `ALLOW_MIGRATIONS=1`, e.g. `ALLOW_MIGRATIONS=1 make m`.'
)


def _strip_heredocs(command):
    """Drop here-document bodies: they are data (a script fed to stdin, a file being written), not commands."""
    lines = []
    delimiter = None
    for line in command.split('\n'):
        if delimiter is not None:
            if line.strip() == delimiter:
                delimiter = None
            continue
        lines.append(line)
        match = HEREDOC.search(line)
        if match:
            delimiter = match.group(2)
    return '\n'.join(lines)


def _tokens(command):
    # Newlines separate commands like `;`, except inside quotes (multi-line commit messages).
    lexer = shlex.shlex(command, posix=True, punctuation_chars=SEPARATORS)
    lexer.whitespace = ' \t\r'
    lexer.whitespace_split = True
    try:
        return list(lexer)
    except ValueError:  # unbalanced quotes: fall back to a plain split, still better than nothing
        return command.split()


def _segments(command):
    """Simple commands separated by newlines, `;`, `&&`, `||`, `|`, `&` and parentheses."""
    segment = []
    for token in _tokens(_strip_heredocs(command)):
        if token and all(char in SEPARATORS for char in token):
            if segment:
                yield segment
            segment = []
        else:
            segment.append(token)
    if segment:
        yield segment


def _is_make(word):
    return word.rsplit('/', 1)[-1] in {'make', 'gmake'}


def _make_targets(args):
    skip = False
    for arg in args:
        if skip:
            skip = False
            continue
        if arg in MAKE_OPTIONS_WITH_VALUE:
            skip = True
            continue
        if arg.startswith('-') or ASSIGNMENT.match(arg):
            continue
        yield arg


def _blocked_segment(segment):
    """The offending command text, or None. Leading `ALLOW_MIGRATIONS=1` allows the segment."""
    words = list(segment)
    assignments = []
    while words and ASSIGNMENT.match(words[0]):
        assignments.append(words.pop(0))
    if ALLOW in assignments:
        return None
    if words and words[0] in {'env', 'command', 'exec', 'time', 'nohup', 'sudo'}:
        return _blocked_segment(words[1:])
    if not words or words[0] in TEXT_COMMANDS:
        return None
    if words[0].rsplit('/', 1)[-1] in SHELLS and '-c' in words[1:]:
        script_index = words.index('-c') + 1
        if script_index < len(words):
            return blocked(words[script_index])
    if _is_make(words[0]) and MAKE_TARGETS & set(_make_targets(words[1:])):
        return ' '.join(segment)
    for index, word in enumerate(words[:-1]):
        if word.rsplit('/', 1)[-1] == 'tortoise' and words[index + 1] in TORTOISE_COMMANDS:
            return ' '.join(segment)
    return None


def blocked(command):
    if command.lstrip().startswith(ALLOW + ' '):
        return None
    for segment in _segments(command):
        hit = _blocked_segment(segment)
        if hit:
            return hit
    return None


def main():
    try:
        payload = json.load(sys.stdin)
    except ValueError:
        return 0
    if payload.get('tool_name') != 'Bash':
        return 0
    command = (payload.get('tool_input') or {}).get('command') or ''
    hit = blocked(command)
    if hit:
        print(MESSAGE.format(command=hit), file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    sys.exit(main())
