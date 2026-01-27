#!/usr/bin/env python3

import subprocess
import os

# Change working dir to the script path
os.chdir(os.path.dirname(os.path.abspath(__file__)))

subprocess.run(['mcrl22lps', '-n', 'WMS.mcrl2', 'WMS.lps'], check=True)
subprocess.run(['lpsreach', '-v', '--chaining', '--groups=simple', '--saturation', 'WMS.lps', 'WMS.sym'], check=True)
subprocess.run(['lps2lts', '-v', '-rjittyc', '--cached', 'WMS.lps', 'WMS.aut'], check=True)


