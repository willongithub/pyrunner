import json
from pathlib import Path

import click
import pendulum
import yaml
from rich import print
from rich.console import Console
from rich.progress import MofNCompleteColumn, Progress, SpinnerColumn
from rich.text import Text
from trogon import tui

from pyrunner import __name__ as name
from pyrunner import __version__ as version
from pyrunner.models import JobConfiguration, RuntimeConfiguration
from pyrunner.utils import CONFIG_TEMPLATE, do_job, get_runtime_info, start_web_ui


@tui(help="Start Terminal User Interface")
@click.group(invoke_without_command=True)
@click.option(
    "--web",
    "-W",
    is_flag=True,
    default=False,
    help="Start Web UI.",
)
@click.option(
    "--yml",
    "-Y",
    help="Specify path to the job configuration YAML file.",
)
@click.option(
    "--template",
    "-T",
    is_flag=True,
    default=False,
    help="Get a template of the configuration file.",
)
@click.option(
    "--verbose",
    "-V",
    is_flag=True,
    default=True,
    help="Show detail info.",
)
def run(web, yml, template, verbose):
    if template:
        output = Path("config_template.yaml")
        output.write_text(CONFIG_TEMPLATE)
        print(f"\nTemplate config file generated at: {str(output)}.\n")
        return

    console = Console()
    title = Text("")
    title.append("\nWelcome to ")
    title.append(f"{name}", style="bold dark_red")
    title.append(" ")
    title.append(f"v{version}\n", style="italic underline")
    console.print(title)

    try:
        if web:
            print("\n>>> Starting Web UI...\n")
            start_web_ui()
            return
    except Exception as e:
        print(f"Fail to start Web UI: {str(e)}")
        return

    while not yml:
        yml = input("Job configuration file: ")
        if not Path(yml).exists():
            print("\n>>> File not exist. Please double-check the path.\n")
            yml = None
    file = Path(yml)

    try:
        if verbose:
            print("\n>>> Runtime info:")
        info = get_runtime_info()
        if verbose:
            Console().print_json(json.dumps(info))
    except Exception as e:
        print(f"Fail to detect Docker engine: {str(e)}")
        return

    try:
        with open(file) as f:
            config = yaml.safe_load(f)
        runtime = RuntimeConfiguration(**config.get("runtime"))
        job_queue = config["job"]
    except Exception as e:
        print(f"Invalid YAMl configuration file: {str(e)}")
        return

    if verbose:
        print("\n>>> Job config:")
        Console().print_json(json.dumps(runtime))
        print("\n>>> Job queue:")
        Console().print_json(json.dumps(job_queue))

    volume = Path(runtime.volume)
    if not volume.exists():
        volume.mkdir(parents=True, exist_ok=True)
        print(f"Input folder mounted at: {str(volume)}. Put files in it and restart.")
        return

    print(f"\n>>> Start: {pendulum.now()}")

    with Progress(
        SpinnerColumn(), MofNCompleteColumn(), *Progress.get_default_columns()
    ) as p:
        job_progress = p.add_task("[orange]Running...", total=len(job_queue))
        for job in job_queue:
            print(f"\n>> {job.get('name', 'No name')}")
            job = JobConfiguration(**job)
            do_job(runtime, job)
            p.update(job_progress, advance=1)

    print(f"\n>>> End: {pendulum.now()}")
