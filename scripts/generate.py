# pylint: disable=line-too-long

import argparse
import bz2
import shutil
import subprocess
import sys
import json

from pathlib import Path as Path
import os
import re


def parse_state_space_output(line: str) -> tuple[int, int] | None:
    """Parse state space generation output to extract states and transitions."""
    match = re.search(r"(\d+)\s+states\s+and\s+(\d+)\s+transitions", line)
    if match:
        states = int(match.group(1))
        transitions = int(match.group(2))
        return (states, transitions)
    return None


def run(path: Path, mcrl2_path: Path, output_path: Path, generated_lts: str):
    """Execute the given run.py script in the given path."""

    print(f"Generating {generated_lts} from {path}")

    run_py = path / "run.py"
    if not run_py.exists():
        raise FileNotFoundError(f"{run_py} not found")

    if os.path.exists(os.path.join(output_path, generated_lts + ".bz2")):
        print(
            f"{generated_lts}.bz2 already exists in {output_path}, skipping generation."
        )
        return

    env = os.environ.copy()
    env["PATH"] = str(mcrl2_path) + os.pathsep + env.get("PATH", "")

    result = {"lts": generated_lts, "contains_tau": False}
    with subprocess.Popen(
        [sys.executable, str(run_py)],
        cwd=str(path),
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        bufsize=1,
    ) as proc:
        if proc.stdout:
            for line in proc.stdout:
                print(line, end="")

                output = parse_state_space_output(line)
                if output:
                    states, transitions = output
                    result["states"] = states
                    result["transitions"] = transitions
                    print(
                        f"Generated LTS with {states} states and {transitions} transitions."
                    )

        proc.wait()
        if proc.returncode != 0:
            raise RuntimeError(
                f"Running {run_py} failed with exit code {proc.returncode}"
            )


    # Copy the generated .aut file to the output location
    generated_file = path / generated_lts
    if not generated_file.exists():
        raise FileNotFoundError(f"{generated_file} not found after running {run_py}")
    
    output_file = output_path / generated_lts
    shutil.move(str(generated_file), str(output_file))
    
    # Check if the resulting .aut file contains tau transitions
    with open(output_file, "r", encoding="utf-8") as f:
        for line in f:
            if "tau" in line:
                result["contains_tau"] = True
                break

    # Write the results to a summary file
    summary_file = output_path / "summary.json"
    with open(summary_file, "a", encoding="utf-8") as f:
        print(result)
        f.write(json.dumps(result) + "\n")

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

    run(
        parsed_args.cases_path / "academic/dining/",
        parsed_args.mcrl2_path,
        parsed_args.output_path,
        "dining_10.aut",
    )
    run(
        parsed_args.cases_path / "academic/food_distribution/",
        parsed_args.mcrl2_path,
        parsed_args.output_path,
        "food_distribution.aut",
    )
    run(
        parsed_args.cases_path / "academic/goback/",
        parsed_args.mcrl2_path,
        parsed_args.output_path,
        "goback.aut",
    )
    run(
        parsed_args.cases_path / "academic/onebit/",
        parsed_args.mcrl2_path,
        parsed_args.output_path,
        "onebit.aut",
    )

    run(
        parsed_args.cases_path / "games/clobber/",
        parsed_args.mcrl2_path,
        parsed_args.output_path,
        "clobber.aut",
    )

    run(
        parsed_args.cases_path / "industrial/1394/",
        parsed_args.mcrl2_path,
        parsed_args.output_path,
        "1394-fin.aut",
    )


if __name__ == "__main__":
    main()
