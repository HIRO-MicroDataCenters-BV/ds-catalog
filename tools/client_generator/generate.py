import os
import sys
import argparse
import subprocess
import tempfile
import shutil
from typing import Dict, Optional


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))

CLIENT_DIR = os.path.join(PROJECT_ROOT, "client")
TEMPLATES_DIR = os.path.join(CURRENT_DIR, "templates")
CONFIG_PATH = os.path.join(CURRENT_DIR, "config.json")


def is_url(value: str) -> bool:
    return value.startswith("http://") or value.startswith("https://")


def generate_openapi(
    file: str,
    volumes: Optional[Dict[str, str]] = None,
    use_asyncio: bool = False,
) -> None:
    docker_args = [
        "docker",
        "run",
        "--rm",
        "-v",
        f"{CLIENT_DIR}:/project",
        "-v",
        f"{TEMPLATES_DIR}:/templates",
        "-v",
        f"{CONFIG_PATH}:/config.json",
    ]
    generator_args = [
        "openapitools/openapi-generator-cli:v7.8.0",
        "generate",
        "-g",
        "python",
        "-t",
        "/templates",
        "-c",
        "/config.json",
        "-o",
        "/project",
        "-i",
        file,
    ]

    if volumes is not None:
        for key, value in volumes.items():
            docker_args += ["-v", f"{key}:{value}"]

    if use_asyncio:
        generator_args += ["--library", "asyncio"]

    subprocess.run([*docker_args, *generator_args], stdout=subprocess.PIPE, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate python client")
    parser.add_argument("file", help="input OpenAPI specification file path or URL")
    parser.add_argument("--asyncio", dest="asyncio", action="store_true",
                        help="generate async code")
    args = parser.parse_args()

    file = str(args.file).strip()
    use_asyncio: bool = args.asyncio

    try:
        if is_url(file):
            generate_openapi(
                file=file,
                use_asyncio=use_asyncio,
            )
        else:
            with tempfile.TemporaryDirectory() as tmp_dir:
                tmp_filename = "openapi.yaml"
                tmp_file_path = os.path.join(tmp_dir, tmp_filename)
                shutil.copyfile(file, tmp_file_path)
                generate_openapi(
                    volumes={tmp_dir: "/openapi"},
                    file=f"/openapi/{tmp_filename}",
                    use_asyncio=use_asyncio,
                )
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        sys.exit(1)

    print("Successfully finished")


if __name__ == "__main__":
    main()
