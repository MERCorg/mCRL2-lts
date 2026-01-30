#!/usr/bin/env python3

import subprocess
import os

# Change working dir to the script path
os.chdir(os.path.dirname(os.path.abspath(__file__)))

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

for model in os.listdir(SCRIPT_DIR):
    if model.endswith(".mcrl2"):
        model = model[:-6]

        subprocess.run(
            ["mcrl22lps", "-v", "--timings", f"{model}.mcrl2", f"{model}.lps"],
            check=True,
        )
        subprocess.run(
            [
                "lpsreach",
                "-v",
                "--saturation",
                "--groups=simple",
                "--chaining",
                f"{model}.lps",
                f"{model}.sym",
            ],
            check=True,
        )
        subprocess.run(
            ["lps2lts", "-v", "-rjittyc", f"{model}.lps", f"{model}.aut"],
            check=True,
        )
