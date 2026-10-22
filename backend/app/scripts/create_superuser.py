import typer

from app.core.database import DatabaseConnection
from app.core.fields.email_field import normalize_email
from app.domains.user.models import User


async def create_superuser():
    email = normalize_email(typer.prompt('Email'))
    first_name = typer.prompt('First name')
    last_name = typer.prompt('Last name')
    password = typer.prompt('Password', hide_input=True, confirmation_prompt=True)
    async with DatabaseConnection():
        user = User(email=email, first_name=first_name, last_name=last_name)
        await user.set_password_async(password)
        user.is_superuser = True
        await user.save()
    typer.echo(f'Creating superuser {first_name} {last_name} with email {email}')
