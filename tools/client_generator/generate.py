import os
import sys
import argparse
import subprocess
import tempfile
import shutil
import json
from typing import Dict, Optional


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))

CLIENT_DIR = os.path.join(PROJECT_ROOT, "client")
TEMPLATES_DIR = os.path.join(CURRENT_DIR, "templates")
CONFIG_PATH = os.path.join(CURRENT_DIR, "config.json")
ARGS_FILE_PATH = os.path.join(CLIENT_DIR, ".openapi-generator", "generator_args.json")


class InvalidArgsException(Exception):
    pass


def is_url(value: str) -> bool:
    return value.startswith("http://") or value.startswith("https://")


class ArgsStore:
    def __init__(self, file_path: str) -> None:
        self._file_path = file_path

    def _ensure_directory_exists(self) -> None:
        directory = os.path.dirname(self._file_path)
        if not os.path.exists(directory):
            os.makedirs(directory)

    def exists(self) -> bool:
        return os.path.exists(self._file_path)

    def save(self, args: argparse.Namespace) -> None:
        self._ensure_directory_exists()
        with open(self._file_path, "w") as f:
            json.dump(vars(args), f)

    def load(self) -> argparse.Namespace:
        with open(self._file_path, "r") as f:
            return argparse.Namespace(**json.load(f))


class ArgsManager:
    def __init__(self, args: argparse.Namespace, store: ArgsStore) -> None:
        self._args = args
        self._store = store

    def get_args(self):
        if self._args.file is None:
            if self._store.exists():
                return self._store.load()
            else:
                raise InvalidArgsException()
        else:
            self._store.save(self._args)

        return self._args


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
        "openapitools/openapi-generator-cli:v7.3.0",
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
    parser.add_argument("--file", help="input OpenAPI specification file path or URL")
    parser.add_argument("--asyncio", dest="asyncio", action="store_true",
                        help="generate async code")
    args = parser.parse_args()

    args_store = ArgsStore(ARGS_FILE_PATH)
    args_manager = ArgsManager(args, args_store)

    try:
        args = args_manager.get_args()
    except InvalidArgsException:
        print("Error: The argument '--file' is not provided, "
              "and there are no saved arguments.")
        sys.exit(1)

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
