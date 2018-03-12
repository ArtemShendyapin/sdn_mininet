#!/usr/bin/python

import sys
from subprocess import check_output
from subprocess import Popen

# This application used to launch background server on each host
ip_addr = str(sys.argv[1])
port = str(sys.argv[2])
command = 'while true; do nc -l ' + ip_addr + ' -p ' + port  + '; done &'
process = Popen(command, shell = True)
p = str(process.pid)
print(p)
