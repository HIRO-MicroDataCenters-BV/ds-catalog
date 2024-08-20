import argparse
import json
import os
import sys

import yaml
from uvicorn.importer import import_from_string


def main() -> None:
    parser = argparse.ArgumentParser(prog="extract-openapi.py")
    parser.add_argument(
        "app",
        help='App import string. Eg. "main:app"',
        default="main:app",
    )
    parser.add_argument(
        "--app-dir",
        help="Directory containing the app",
        default=None,
    )
    parser.add_argument(
        "--out",
        help="Output file ending in .json or .yaml",
        default="openapi.yaml",
    )
    parser.add_argument(
        "--app_version",
        help="App version",
        default=None,
    )
    parser.add_argument(
        "--app_version_file",
        help="App version file",
        default=None,
    )

    args = parser.parse_args()

    if args.app_dir is not None:
        print(f"adding {args.app_dir} to sys.path")
        sys.path.insert(0, args.app_dir)

    print(f"importing app from {args.app}")
    app = import_from_string(args.app)
    openapi = app.openapi()

    app_version = None
    if args.app_version is not None:
        app_version = args.app_version
    elif args.app_version_file is not None:
        with open(args.app_version_file, 'r') as f:
            app_version = f.read().strip()

    if app_version is not None:
        openapi["info"]["version"] = app_version

    print("writing openapi spec")
    dir = os.path.dirname(args.out)
    if dir:
        os.makedirs(dir, exist_ok=True)

    with open(args.out, "w") as f:
        if args.out.endswith(".json"):
            json.dump(openapi, f, indent=2)
        else:
            yaml.dump(openapi, f, sort_keys=False)

    print(f"spec written to {args.out}")


if __name__ == "__main__":
    main()
