import json
from pathlib import Path

import click
import subprocess
import pendulum
import yaml
from rich.console import Console
from rich.progress import MofNCompleteColumn, Progress, SpinnerColumn
from rich.text import Text

from pyrunner import __name__ as name
from pyrunner import __version__ as version


@click.command()
@click.option(
    "--yml",
    "-Y",
    default="./config.yaml",
    help="Specify path to configuration YAML file.",
)
@click.option(
    "--data",
    "-D",
    default="data",
    help="Specify data folder mounted on container.",
)
def run(yml, data):
    console = Console()
    title = Text("")
    title.append(f"\nWelcome to ")
    title.append(f"{name}", style="bold dark_red")
    title.append(f" ")
    title.append(f"v{version}\n", style="italic underline")
    console.print(title)

    file = Path(yml)
    volume = Path(data)

    if data:
        volume.mkdir(parents=True, exist_ok=True)

    if not file.exists():
        click.echo("Please specify YAMl configuration file.")
        return

    try:
        with open(file) as f:
            config = yaml.safe_load(f)
    except Exception as e:
        click.echo("Invalid YAMl configuration file.")
        return

    click.echo("\n>> Docker runtime:")
    Console().print_json(json.dumps(config["runtime"]))
    click.echo("\n>> Job queue:")
    Console().print_json(json.dumps(config["job"]))

    click.echo(f"\n>> Start: {pendulum.now()}")

    subprocess.call([
        "docker", "run", "--rm",
        "-v", f"{Path.cwd()}/data:/app/data",
        "qa:latest",
        "python3.8 -m qa --help"
    ])

    click.echo(f"\n>> End: {pendulum.now()}")
