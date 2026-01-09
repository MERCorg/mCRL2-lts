#!/usr/bin/env python3

import subprocess
import os

# Change working dir to the script path
os.chdir(os.path.dirname(os.path.abspath(__file__)))

subprocess.run(['mcrl22lps', 'hopcroft.mcrl2', 'hopcroft.lps'], check=True)
subprocess.run(['lps2lts', '-v', 'hopcroft.lps', '--no-info', 'hopcroft.aut'], check=True)
