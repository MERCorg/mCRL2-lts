# pylint: disable=line-too-long

import argparse
import bz2
import shutil
import subprocess
import sys

from pathlib import Path as Path
import os

def run(path: Path, mcrl2_path: Path, output_path: Path, generated_lts: str):
    """Execute the given run.py script in the given path."""

    print(f"Generating {generated_lts} from {path}")

    run_py = path / "run.py"
    if not run_py.exists():
        raise FileNotFoundError(f"{run_py} not found")

    env = os.environ.copy()
    env["PATH"] = str(mcrl2_path) + os.pathsep + env.get("PATH", "")
    proc = subprocess.run([sys.executable, str(run_py)], cwd=str(path), check=True, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in proc.stdout:
        print(line.decode(), end="")

    # Copy the generated .aut file to the output location
    generated_file = path / generated_lts
    if not generated_file.exists():
        raise FileNotFoundError(f"{generated_file} not found after running {run_py}")

    output_file = output_path / generated_lts
    shutil.move(str(generated_file), str(output_file))

    # Compress the .aut file with bz2
    with open(output_file, "rb") as f_in:
        with bz2.open(f"{output_file}.bz2", "wb") as f_out:
            f_out.writelines(f_in)

    # Delete the original .aut file
    output_file.unlink()

def main():
    args = argparse.ArgumentParser(
        description="Generate .aut files based on the examples."
    )
    args.add_argument("mcrl2_path", help="Path to the mCRL2 installation.", type=Path)
    args.add_argument("cases_path", help="Path to the cases directory.", type=Path)
    args.add_argument("output_path", help="Path to the output directory.", type=Path)
    parsed_args = args.parse_args()

    run(parsed_args.cases_path / "academic/dining/", parsed_args.mcrl2_path, parsed_args.output_path, "dining_10.aut")
    run(parsed_args.cases_path / "academic/food_distribution/", parsed_args.mcrl2_path, parsed_args.output_path, "food_distribution.aut")
    run(parsed_args.cases_path / "academic/go_back/", parsed_args.mcrl2_path, parsed_args.output_path, "go_back.aut")
    run(parsed_args.cases_path / "academic/hopcroft/", parsed_args.mcrl2_path, parsed_args.output_path, "hopcroft.aut")
    run(parsed_args.cases_path / "academic/onebit/", parsed_args.mcrl2_path, parsed_args.output_path, "onebit.aut")

    run(parsed_args.cases_path / "games/clobber/", parsed_args.mcrl2_path, parsed_args.output_path, "clobber.aut")

    run(parsed_args.cases_path / "industrial/1394/", parsed_args.mcrl2_path, parsed_args.output_path, "1394-fin.aut")


if __name__ == "__main__":
    main()
