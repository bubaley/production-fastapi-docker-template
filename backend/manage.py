import ast
import asyncio
import code
import importlib
import inspect
import subprocess  # nosec B404
import sys

import typer
from tortoise import Tortoise
from tortoise.expressions import Case, F, Q, Value, When

from app import scripts
from app.core.database import MODELS, DatabaseConnection

app = typer.Typer()


@app.callback()
def main():
    pass


@app.command(name='create_superuser')
def create_superuser():
    typer.echo('Creating superuser...')
    asyncio.run(scripts.create_superuser())


@app.command(
    name='test',
    context_settings={'allow_extra_args': True, 'ignore_unknown_options': True},
)
def run_tests(
    ctx: typer.Context,
    path: str = typer.Argument('app', help='Path to tests or specific test file'),
):
    """
    Run pytest for the specified path (defaults to 'app').

    Extra arguments are forwarded to pytest, e.g.:

        manage.py test app --keepdb
        manage.py test app/domains/post/tests -x -k test_foo
    """
    typer.echo(f'Running tests in: {path}')
    cmd = [sys.executable, '-m', 'pytest', path, '-s', *ctx.args]
    result = subprocess.run(cmd)  # nosec B603
    sys.exit(result.returncode)


@app.command(name='shell')
def shell():
    """Start an interactive Python shell with all models pre-imported (like Django shell)."""
    import tortoise.models as _tortoise_models

    shell_locals: dict = {
        'asyncio': asyncio,
        'Q': Q,
        'F': F,
        'Case': Case,
        'When': When,
        'Value': Value,
    }
    for module_path in MODELS:
        module = importlib.import_module(module_path)
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if (
                issubclass(obj, _tortoise_models.Model)
                and obj is not _tortoise_models.Model
                and obj.__module__ == module.__name__
            ):
                shell_locals[name] = obj

    model_list = '\n'.join(f'  - {name}' for name in sorted(shell_locals))
    banner = f'Tortoise ORM Shell\n\nImported:\n{model_list}\n\nHint: use await directly, e.g.  await User.all()'

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(DatabaseConnection().tortoise_init())

    try:
        from IPython import embed  # type: ignore

        embed(banner1=banner, user_ns=shell_locals, using='asyncio')
    except ImportError:

        class AsyncConsole(code.InteractiveConsole):
            """Fallback console with top-level await support via PyCF_ALLOW_TOP_LEVEL_AWAIT."""

            def __init__(self, locals, loop):
                super().__init__(locals=locals)
                self.compile.compiler.flags |= ast.PyCF_ALLOW_TOP_LEVEL_AWAIT
                self._loop = loop

            def runcode(self, code):
                try:
                    result = eval(code, self.locals)  # nosec B307
                    if asyncio.iscoroutine(result):
                        self._loop.run_until_complete(result)
                except SystemExit:
                    raise
                except Exception:
                    self.showtraceback()

        typer.echo(banner)
        try:
            import readline
            import rlcompleter

            readline.set_completer(rlcompleter.Completer(shell_locals).complete)
            # macOS ships libedit instead of GNU readline — different binding syntax
            if readline.__doc__ and 'libedit' in readline.__doc__:
                readline.parse_and_bind('bind ^I rl_complete')
            else:
                readline.parse_and_bind('tab: complete')
        except ImportError:
            pass
        AsyncConsole(shell_locals, loop).interact(banner='')
    finally:
        loop.run_until_complete(Tortoise.close_connections())
        loop.close()


if __name__ == '__main__':
    app()
