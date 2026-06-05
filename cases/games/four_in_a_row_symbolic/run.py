#!/usr/bin/env python3

import subprocess
import os

# Change working dir to the script path
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# We apply various preprocessing steps to eliminate the Board and Row parameters
# since they are complex data types, in this case lists.
run = subprocess.run(
    ["mcrl22lps", "-v", "-n", "-f", "four_in_a_row_symbolic.mcrl2"],
    stdout=subprocess.PIPE,
    check=True,
)
run = subprocess.run(
    ["lpssuminst", "-v"], input=run.stdout, stdout=subprocess.PIPE, check=True
)
run = subprocess.run(
    ["lpsparunfold", "-sBoard", "-n6"],
    input=run.stdout,
    stdout=subprocess.PIPE,
    check=True,
)
run = subprocess.run(
    ["lpsparunfold", "-sRow", "-n8"],
    input=run.stdout,
    stdout=subprocess.PIPE,
    check=True,
)
run = subprocess.run(
    ["lpsrewr", "-v"], input=run.stdout, stdout=subprocess.PIPE, check=True
)
subprocess.run(["lpsconstelm", "-v", "-", "four_in_a_row_symbolic.lps"], input=run.stdout, check=True)
subprocess.run(
    [
        "lpsreach",
        "-v",
        "--groups=simple",
        "--reorder=42 35 28 21 14 7 0 36 29 22 15 8 1 37 30 23 16 9 2 38 31 24 17 10 3 39 32 25 18 11 4 40 33 26 19 12 5 41 34 27 20 13 6",
        "four_in_a_row_symbolic.lps",
        "four_in_a_row_symbolic.sym",
    ],
    check=True,
)
