import typer

from app.core.database import DatabaseConnection
from app.domains.user.models import User


async def create_superuser():
    email = typer.prompt('Email')
    first_name = typer.prompt('First name')
    last_name = typer.prompt('Last name')
    password = typer.prompt('Password', hide_input=True, confirmation_prompt=True)
    async with DatabaseConnection():
        user = User(email=email, first_name=first_name, last_name=last_name, password=password)
        user.set_password(password)
        user.is_superuser = True
        await user.save()
    typer.echo(f'Creating superuser {first_name} {last_name} with email {email}')
