#!/usr/bin/env python3

import subprocess
import os

from sys import argv

# Change working dir to the script path
os.chdir(os.path.dirname(os.path.abspath(__file__)))

mcrl22lps = subprocess.run(['mcrl22lps', '-vn', 'hex.mcrl2', 'hex.lps'], stdout=subprocess.PIPE, check=True)
subprocess.run(['lps2lts', '-v', '-rjittyc', 'hex.lps', 'hex.aut'], check=True)
