import json
from pathlib import Path

from pyrunner.utils import get_runtime_info, do_job
import click
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
@click.option(
    "--verbose",
    "-V",
    is_flag=True,
    default=True,
    help="Display detail info.",
)
def run(yml, data, verbose):
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
        if verbose: click.echo("\n>>> Runtime info:")
        info = get_runtime_info()
        if verbose: Console().print_json(json.dumps(info))
    except Exception as e:
        click.echo(f"Fail to detect Docker engine: {str(e)}")
        return
    
    try:
        with open(file) as f:
            config = yaml.safe_load(f)
        engine = config["engine"]
        job_queue = config["job"]
    except Exception as e:
        click.echo(f"Invalid YAMl configuration file: {str(e)}")
        return

    if verbose: 
        click.echo("\n>>> Job config:")
        Console().print_json(json.dumps(engine))
        click.echo("\n>>> Job queue:")
        Console().print_json(json.dumps(job_queue))

    click.echo(f"\n>>> Start: {pendulum.now()}")

    with Progress(
            SpinnerColumn(), MofNCompleteColumn(), *Progress.get_default_columns()
        ) as p:
            job_progress = p.add_task("[orange]Running...", total=len(job_queue))
            for job in job_queue:
                click.echo(f"\n>> {job['name']}")
                do_job(engine, job)
                p.update(job_progress, advance=1)

    click.echo(f"\n>>> End: {pendulum.now()}")
