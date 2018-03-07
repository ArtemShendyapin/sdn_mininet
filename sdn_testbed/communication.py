#!/usr/bin/python

import sys
from subprocess import check_output
from subprocess import Popen

ip_addr = str(sys.argv[1])
mode = str(sys.argv[2])
if mode == 'server':
    command = 'iperf3 -s -B ' + ip_addr + ' -i 1 &'
else:
    command = 'iperf3 -c ' + ip_addr + ' -u -b 100M -i 1 -t 20 &'
process = Popen(command, shell = True)
p = str(process.pid)
print(p)
