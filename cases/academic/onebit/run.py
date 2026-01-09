#!/usr/bin/env python3

import subprocess
import os

# Change working dir to the script path
os.chdir(os.path.dirname(os.path.abspath(__file__)))

subprocess.run(['mcrl22lps', '-v', 'onebit.mcrl2', 'onebit.lps'], check=True)
subprocess.run(['lps2lts', '-v', 'onebit.lps', 'onebit.aut'], check=True)