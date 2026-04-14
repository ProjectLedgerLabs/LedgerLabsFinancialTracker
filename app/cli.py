# cli.py

import click
from app.database import create_db_and_tables, get_cli_session
from app.repositories.user import UserRepository
from app.utilities.security import encrypt_password
from app.models.user import UserBase


def initialize():
  
    create_db_and_tables()

    with get_cli_session() as session:
        user_repo = UserRepository(session)

        # Check if user already exists
        existing_user = user_repo.get_by_username("bob")
        if existing_user:
            click.echo("User 'bob' already exists.")
            return existing_user

        # Create new user
        user_data = UserBase(
            username="bob",
            email="bob@example.com",
            password=encrypt_password("bobpass"),  # adjust if model expects hashed_password
        )

        click.echo("Creating initial user account: bob")
        new_user = user_repo.create(user_data)
        session.commit()  # ensure persistence if not handled inside create()
        return new_user


@click.group()
def cli():
    
    pass


@cli.command()
def init():
    
    initialize()


if __name__ == "__main__":
    cli()
