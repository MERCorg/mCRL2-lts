# pylint: disable=line-too-long
# ruff: line-length=240

import argparse
import bz2
import shutil
import subprocess
import sys
import json
import time
from typing import Any

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


def run(
    path: Path,
    mcrl2_path: Path,
    output_path: Path,
    generated_lts: list[str],
    pretty_print_lps: list[str],
):
    """Execute the given run.py script in the given path."""

    print(f"Generating {generated_lts} from {path}")

    ltsinfo_path = shutil.which("ltsinfo", path=str(mcrl2_path))
    if ltsinfo_path is None:
        raise FileNotFoundError("ltsinfo not found in the given mCRL2 path")

    lpspp_path = shutil.which("lpspp", path=str(mcrl2_path))
    if lpspp_path is None:
        raise FileNotFoundError("lpspp not found in the given mCRL2 path")

    run_py = path / "run.py"
    if not run_py.exists():
        raise FileNotFoundError(f"{run_py} not found")

    # Check if the .aut files are already generated#
    already_generated = True
    for file in generated_lts:
        if file.endswith(".aut"):
            # For .aut check .aut.bz2 existence
            if not (output_path / "explicit" / f"{file}.bz2").exists():
                already_generated = False
        else:
            # Else check the file directly
            if not (output_path / "symbolic" / file).exists():
                already_generated = False

    if already_generated:
        print(f"{generated_lts} already generated, skipping.")
        return

    env = os.environ.copy()
    env["PATH"] = str(mcrl2_path) + os.pathsep + env.get("PATH", "")

    run_start = time.monotonic()
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

        proc.wait()
        if proc.returncode != 0:
            raise RuntimeError(
                f"Running {run_py} failed with exit code {proc.returncode}"
            )
    run_time = time.monotonic() - run_start

    lps_output_path = output_path / "lps"
    lps_output_path.mkdir(parents=True, exist_ok=True)

    for lps_name in pretty_print_lps:
        source_lps = path / lps_name
        if not source_lps.exists():
            raise FileNotFoundError(f"{source_lps} not found after running {run_py}")

        pretty_lps_filename = f"{Path(lps_name).stem}.lps.txt"
        pretty_lps = lps_output_path / pretty_lps_filename
        with open(pretty_lps, "w", encoding="utf-8") as lps_out:
            with subprocess.Popen(
                [lpspp_path, str(source_lps)],
                text=True,
                stdout=lps_out,
                bufsize=1,
            ) as proc:
                proc.wait()
                if proc.returncode != 0:
                    raise RuntimeError(
                        f"Running lpspp on {source_lps} failed with exit code {proc.returncode}"
                    )

    # Copy generated artefacts to output, and collect metadata.
    for file in generated_lts:
        result: dict[str, Any] = {"lts": file, "run_time": run_time}

        generated_file = path / file
        if not generated_file.exists():
            raise FileNotFoundError(f"{generated_file} not found after running {run_py}")

        if Path(file).suffix == ".aut":
            file_output_path = output_path / "explicit"
        else:
            file_output_path = output_path / "symbolic"
        file_output_path.mkdir(parents=True, exist_ok=True)

        output_file = file_output_path / file
        shutil.move(str(generated_file), str(output_file))

        if output_file.suffix == ".aut":
            result["contains_tau"] = False
            # Check if the resulting .aut file contains tau transitions
            with open(output_file, "r", encoding="utf-8") as f:
                for line in f:
                    if "tau" in line:
                        result["contains_tau"] = True
                        break

            # Obtain the number of states and transitions from ltsinfo
            with subprocess.Popen(
                [ltsinfo_path, str(output_file)],
                text=True,
                stdout=subprocess.PIPE,
                bufsize=1
            ) as proc:
                if proc.stdout:
                    for line in proc.stdout:
                        parsed = parse_state_space_output(line)
                        if parsed:
                            states, transitions = parsed
                            result["states"] = states
                            result["transitions"] = transitions

                proc.wait()
                if proc.returncode != 0:
                    raise RuntimeError(
                        f"Running ltsinfo on {output_file} failed with exit code {proc.returncode}"
                    )
                
            # Fail if the state or transitions cannot be obtained
            if "states" not in result or "transitions" not in result:
                raise RuntimeError(f"Could not obtain states and transitions from ltsinfo output for {output_file}")

            # Compress the .aut file with bz2
            compress_start = time.monotonic()
            with open(output_file, "rb") as f_in:
                with bz2.open(f"{output_file}.bz2", "wb") as f_out:
                    f_out.writelines(f_in)
            result["compress_time"] = time.monotonic() - compress_start

            # Delete the original .aut file
            output_file.unlink()

        # Write the results to a summary file
        summary_file = output_path / "summary.json"
        with open(summary_file, "a", encoding="utf-8") as f:
            print(result)
            f.write(json.dumps(result) + "\n")

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
        ["dining_10.aut"],
        ["dining_10.lps"],
    )
    run(
        parsed_args.cases_path / "academic/food_distribution/",
        parsed_args.mcrl2_path,
        parsed_args.output_path,
        ["food_distribution.aut"],
        ["food_package.lps"],
    )
    run(
        parsed_args.cases_path / "academic/goback/",
        parsed_args.mcrl2_path,
        parsed_args.output_path,
        ["goback.aut"],
        ["goback.lps"],
    )
    run(
        parsed_args.cases_path / "academic/non-atomic_registers/",
        parsed_args.mcrl2_path,
        parsed_args.output_path,
        ["Aravind_BLRU.aut",
         "Aravind_BLRU.sym",
         "Dijkstra.aut",
         "Dijkstra.sym",
         "Lamport_3-bit.aut",
         "Lamport_3-bit.sym",
         "Lamport_3-bit_incorrect_z.aut",
         "Lamport_3-bit_incorrect_z.sym",
         "Szymanski_3-bit_lin_wait.aut",
         "Szymanski_3-bit_lin_wait.sym",
         "Szymanski_3-bit_lin_wait_alt.aut",
         "Szymanski_3-bit_lin_wait_alt.sym",
         "Szymanski_flag.aut",
         "Szymanski_flag.sym",
         "Szymanski_flag_bit.aut",
         "Szymanski_flag_bit.sym",
         "Szymanski_flag_bit_altexit.aut",
         "Szymanski_flag_bit_altexit.sym"],
        ["Aravind_BLRU.lps",
         "Dijkstra.lps",
         "Lamport_3-bit.lps",
         "Lamport_3-bit_incorrect_z.lps",
         "Szymanski_3-bit_lin_wait.lps",
         "Szymanski_3-bit_lin_wait_alt.lps",
         "Szymanski_flag.lps",
         "Szymanski_flag_bit.lps",
         "Szymanski_flag_bit_altexit.lps"],
    )
    run(
        parsed_args.cases_path / "academic/onebit/",
        parsed_args.mcrl2_path,
        parsed_args.output_path,
        ["onebit.aut"],
        ["onebit.lps"],
    )
    run(
        parsed_args.cases_path / "academic/swp/",
        parsed_args.mcrl2_path,
        parsed_args.output_path,
        ["swp_with_tanenbaums_bug.sym"],
        ["swp_with_tanenbaums_bug.lps"],
    )

    run(
        parsed_args.cases_path / "games/clobber/",
        parsed_args.mcrl2_path,
        parsed_args.output_path,
        ["clobber.aut"],
        ["clobber.lps"],
    )
    run(
        parsed_args.cases_path / "games/domineering/",
        parsed_args.mcrl2_path,
        parsed_args.output_path,
        ["domineering.aut"],
        ["domineering.lps"],
    )
    run(
        parsed_args.cases_path / "games/four_in_a_row_symbolic/",
        parsed_args.mcrl2_path,
        parsed_args.output_path,
        ["four_in_a_row_symbolic.sym"],
        ["four_in_a_row_symbolic.lps"],
    )
    run(
        parsed_args.cases_path / "games/game_of_goose/",
        parsed_args.mcrl2_path,
        parsed_args.output_path,
        ["game_of_goose.aut"],
        ["game_of_goose.lps"],
    )
    run(
        parsed_args.cases_path / "games/hex/",
        parsed_args.mcrl2_path,
        parsed_args.output_path,
        ["hex.aut"],
        ["hex.lps"],
    )
    run(
        parsed_args.cases_path / "games/knights/",
        parsed_args.mcrl2_path,
        parsed_args.output_path,
        ["knights.aut"],
        ["knights.lps"],
    )

    run(
        parsed_args.cases_path / "industrial/1394/",
        parsed_args.mcrl2_path,
        parsed_args.output_path,
        ["1394-fin.aut"],
        ["1394-fin.lps"],
    )

    run(
        parsed_args.cases_path / "industrial/WMS/",
        parsed_args.mcrl2_path,
        parsed_args.output_path,
        ["WMS.aut", "WMS.sym"],
        ["WMS.lps"],
    )

if __name__ == "__main__":
    main()
