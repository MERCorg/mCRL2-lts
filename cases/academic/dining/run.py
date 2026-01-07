#!/usr/bin/env python3

import subprocess
import os

# Change working dir to the script path
os.chdir(os.path.dirname(os.path.abspath(__file__)))

subprocess.run(['mcrl22lps', 'dining_10.mcrl2', 'dining_10.lps'], check=True)

subprocess.run(['lps2lts', 'dining_10.lps', 'dining_10.aut'], check=True)
