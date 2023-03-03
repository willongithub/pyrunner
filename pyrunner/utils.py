import subprocess
from pathlib import Path

import json
import click
import docker
from rich.console import Console


def get_runtime_info() -> dict:
    client = docker.from_env()
    info = client.info()
    version = client.version()
    runtime = {
        "Platform": version["Platform"]["Name"],
        "Engine": version["Version"],
        "OS": version["Os"],
        "Architecture": version["Arch"],
        "CPUs": info["NCPU"],
        "RAM": get_ram(info["MemTotal"]),
    }
    return runtime


def get_ram(bytes) -> str:
    factor = 1024
    ram = ""
    for order in ["", "K", "M", "G", "T", "P"]:
        ram = f"{bytes:.2f} {order}B"
        if bytes < factor:
            break
        bytes /= factor
    return ram


def do_job(engine: dict, job: dict) -> None:
    Console().print_json(json.dumps(job["flags"]))
    cmd = [
        "docker",
        "run",
        "--rm",
        "-it",
        "--shm-size=8G",
        "-v",
        f"{Path.cwd()}/{engine['volume']}:/app/data",
    ]
    if "cpus" in list(engine.keys()):
        cmd.append(f"--cpus={engine['cpus']}")
    if "memory" in list(engine.keys()):
        cmd.append(f"--memory={engine['memory']}")
    if "pull" in list(engine.keys()):
        if engine["pull"]:
            cmd.append("--pull=always")
    cmd.append(engine["image"])
    entrypoint = engine["entrypoint"]
    for flag, value in job["flags"].items():
        entrypoint += f" --{flag} {value}"
    cmd.append(entrypoint)
    subprocess.call(cmd)
