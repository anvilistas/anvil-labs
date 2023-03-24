# SPDX-License-Identifier: MIT
# Copyright (c) 2021 anvilistas


import argparse
import logging
import pathlib
import re
from configparser import ConfigParser

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def read_bumpversion_config(config_file):
    config = ConfigParser()
    config.read(config_file)
    current_version = config.get("bumpversion", "current_version")

    patterns = []
    for section in config.sections():
        if section.startswith("bumpversion:glob:"):
            pattern = section[len("bumpversion:glob:") :]
            patterns.append(pattern)

    glob_patterns = patterns or ["**/*.py"]
    return current_version, glob_patterns


def update_version_in_file(file_path, current_version):
    with open(file_path, "r") as file:
        content = file.read()

    logging.info(f"  Updating version in file: {file_path}")

    version_line = f'__version__ = "{current_version}"'

    if re.search(r'^__version__\s*=\s*"[^"]+"', content, flags=re.MULTILINE):
        logging.info("    Version found")
        updated_content = re.sub(
            r'^__version__\s*=\s*"[^"]+"', version_line, content, flags=re.MULTILINE
        )

    else:
        logging.info("    No version found")
        lines = content.splitlines()
        insert_position = 0

        for i, line in enumerate(lines):
            if (
                not line
                or line.startswith("#")
                or line.startswith("import")
                or line.startswith("from")
            ):
                insert_position = i + 1
            else:
                break

        lines.insert(insert_position, version_line + "\n")
        updated_content = "\n".join(lines)

    if content != updated_content:
        with open(file_path, "w") as file:
            file.write(updated_content)
            logging.info(f"Updated version in {file_path}")


def process_files_or_directory(path, current_version, all_files):
    path = pathlib.Path(path).resolve()

    if path.is_file():
        logging.info(f"Processing file: {path}")
        if str(path) in all_files:
            update_version_in_file(str(path), current_version)
    elif path.is_dir():
        logging.info(f"Processing dir: {path}")
        for file_path in path.glob("**/*.py"):
            if str(file_path) not in all_files:
                continue
            update_version_in_file(str(file_path), current_version)
    else:
        logging.info(f"Error: {path} is not a file or directory")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="*", help="Files or directories to process")
    parser.add_argument(
        "--config",
        default=".bumpversion.cfg",
        help="Path to the bumpversion configuration file",
    )
    args = parser.parse_args()

    config_file = args.config
    current_version, glob_patterns = read_bumpversion_config(config_file)
    # Use the current working directory as the root directory
    root_dir = pathlib.Path.cwd()

    all_files = [str(p) for pattern in glob_patterns for p in root_dir.glob(pattern)]

    for path in args.paths:
        process_files_or_directory(
            path, current_version=current_version, all_files=all_files
        )
