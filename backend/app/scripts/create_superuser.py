import typer
from pydantic import TypeAdapter, ValidationError

from app.core.database import DatabaseConnection
from app.core.fields.email_field import NormalizedEmail
from app.core.fields.password_field import NewPassword
from app.domains.user.models import User


def _prompt_valid(label: str, adapter: TypeAdapter, **prompt_kwargs) -> str:
    while True:
        try:
            return adapter.validate_python(typer.prompt(label, **prompt_kwargs))
        except ValidationError as e:
            typer.echo(e.errors()[0]['msg'], err=True)


async def create_superuser():
    email = _prompt_valid('Email', TypeAdapter(NormalizedEmail))
    first_name = typer.prompt('First name')
    last_name = typer.prompt('Last name')
    password = _prompt_valid('Password', TypeAdapter(NewPassword), hide_input=True, confirmation_prompt=True)
    async with DatabaseConnection():
        user = User(email=email, first_name=first_name, last_name=last_name)
        await user.set_password_async(password)
        user.is_superuser = True
        await user.save()
    typer.echo(f'Creating superuser {first_name} {last_name} with email {email}')
