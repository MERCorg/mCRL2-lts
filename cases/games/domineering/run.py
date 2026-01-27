#!/usr/bin/env python3

import subprocess
import os

from sys import argv

# Change working dir to the script path
os.chdir(os.path.dirname(os.path.abspath(__file__)))

subprocess.run(['mcrl22lps', '-vD', 'domineering.mcrl2', 'domineering.lps'], check=True)
subprocess.run(['lps2lts', '-rjittyc', '-v', 'domineering.lps', 'domineering.aut'], check=True)
