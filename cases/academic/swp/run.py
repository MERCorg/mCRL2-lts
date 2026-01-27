#!/usr/bin/env python3

import subprocess
import os

# Change working dir to the script path
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# SWP with Tanenbaum's bug
subprocess.run(['mcrl22lps', '-v', 'swp_with_tanenbaums_bug.mcrl2', 'swp_with_tanenbaums_bug.lps'], check=True)
subprocess.run(['lpsreach', '-v', '--cached', '--chaining', '--saturation', 'swp_with_tanenbaums_bug.lps', 'swp_with_tanenbaums_bug.sym'], check=True)
