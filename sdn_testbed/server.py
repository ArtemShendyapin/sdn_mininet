#!/usr/bin/python

import sys
from subprocess import check_output
from subprocess import Popen

ip_addr = str(sys.argv[1])
port = str(sys.argv[2])
command = 'nc -l ' + ip_addr + ' -p ' + port  + ' &'
process = Popen(command, shell = True)
p = str(process.pid)
print(p)
