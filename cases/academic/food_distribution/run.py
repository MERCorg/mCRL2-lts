#!/usr/bin/env python3

import subprocess
import os

from sys import argv

# Change working dir to the script path
os.chdir(os.path.dirname(os.path.abspath(__file__)))

run = subprocess.run(['mcrl22lps', 'food_package.mcrl2'], stdout=subprocess.PIPE, check=True)
run = subprocess.run(['lpssuminst', '-', 'food_package.lps'], input=run.stdout, check=True)

subprocess.run(['lps2lts', 'food_package.lps', 'food_distribution.aut', '-rjittyc', '--cached', '-v'], check=True)