import yaml
import json
import click
import docker
from pathlib import Path
from rich.console import Console
from rich.progress import MofNCompleteColumn, Progress, SpinnerColumn


@click.command()
@click.option(
    "--yml",
    "-Y",
    default="config.yaml",
    help="Specify path to configuration YAML file.",
)
def run(yml):
    file = Path(yml)

    if file.suffix not in ["yml", "yaml"] or not file.exist():
        click.echo("Please provide YAMl configuration.")

    with open(file) as f:
        config = yaml.safe_load(f)

    Console().print_json(json.dumps(config))
