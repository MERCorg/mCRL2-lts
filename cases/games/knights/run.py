#!/usr/bin/env python3

import subprocess
import os

# Change working dir to the script path
os.chdir(os.path.dirname(os.path.abspath(__file__)))

run = subprocess.run(['mcrl22lps', '-v', 'knights.mcrl2'], stdout=subprocess.PIPE, check=True)
run = subprocess.run(['lpssuminst'], input=run.stdout, stdout=subprocess.PIPE, check=True)
run = subprocess.run(['lpsparunfold', '-v', '-n1', '-sBoard'], input=run.stdout, stdout=subprocess.PIPE, check=True)
run = subprocess.run(['lpsparunfold', '-v', '-n5', '-sRow', '-', 'knights.lps'], input=run.stdout, check=True)

subprocess.run(['lps2lts', '-rjittyc', '-v', 'knights.lps', 'knights.aut'], check=True)