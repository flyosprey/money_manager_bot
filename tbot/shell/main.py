import sys

import click
from click import Context
from pydantic import ValidationError

from money_manager.config import Config
from tbot.shell.commands.monobank import run_monobank_refresh


@click.group()
@click.option(
    "--env-file", "-e", type=click.STRING, default=".env.dev", help="Load .env file"
)
@click.pass_context
def cli(ctx: Context, env_file: str):
    try:
        ctx.obj = Config(_env_file=env_file)
    except ValidationError as e:
        click.echo(f"Failed to configure application: {e}", err=True)
        sys.exit(2)


def main():
    cli.add_command(run_monobank_refresh)

    cli()


if __name__ == "__main__":
    main()
