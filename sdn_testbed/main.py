#!/usr/bin/env python

from subprocess import call
from time import sleep

from sdntestbed.controller import Runos
from sdntestbed.test import MulticastTest
from sdntestbed.network import Network
from sdntestbed.testcase import Attack
from sdntestbed.testcase import TestCase
from sdntestbed.activity2 import UnicastActivity

if __name__ == '__main__':
    
    controller_list = Runos("127.0.0.1","8080", ssh="root@127.0.0.1")
    bound_sw = ['sw1', 'sw4', 'sw9', 'sw10', 'sw10', 'sw17', 'sw28', 'sw30']
    unbound_names = []
    with Network('../GtsPoland.gml', controller_list, bound_sw, unbound_names) as network:
        unbound_sw = []
        for name in unbound_names:
          unbound_sw.append(network.getNodeByName(name))

        host_list = [network.getNodeByName('h' + str(i)) for i in range(1, len(bound_sw) + 1)]
        test = UnicastActivity(controller_list, network, host_list)

        atk_host = network.getNodeByName('h4')
        attacks = [
      Attack('00:00:00:00:00:01', 'any', 1, 'duplicate', atk_host, host_list),
      Attack('00:00:00:00:00:02', 
             '00:00:00:00:00:03', 2, 'MitM', atk_host, host_list),
      Attack('00:00:00:00:00:01', 'any', 3, 'flood', atk_host),
      Attack('00:00:00:00:00:02', 'any', 2, 'drop', atk_host),
#           Attack('00:00:00:00:00:03', 'any', 2, 'flood'),
      Attack('00:00:00:00:00:04', 'any', 3, 'incorrect_forwarding', atk_host),
#           Attack('00:00:00:00:00:07', 'any', 3, 'drop'),
          ]
#"python ../attacker/attacker.py sw12 00:00:00:00:00:02 00:00:00:00:00:03 drop"]
        attacker = TestCase(attacks, unbound_sw, network)
        phase_num = 7
        for phase in range(phase_num):
          test.start()
          if phase == 0:
            test.listen()
          attacker.start_attacks(phase)
          sleep(25)
          test.stop()
          test.__init__(controller_list, network, host_list)
        test.stop_listen()
        attacker.stop_attacks()
        network._CLI()
"""
    call('mkdir .tmp > /dev/null 2>&1', shell=True)
    
    network_list = xrange(1,26,5) #[1, 5, 10, 15, 20, 25]
    host_list = lambda netsize: [netsize/2+1] #range(1,netsize+1,netsize/10 if netsize/10!=0 else 1) #[1]
    group_list = xrange(1,11,1)#xrange(0,105,5) #[1,10,50,130,250]
    
    test = MulticastTest(controller_list, network_list, host_list, group_list, tmp_folder="/tmp")
    
    test.connection_time_test()
    test.reconnection_time_test()
    
    call('rm -rf .tmp/ > /dev/null 2>&1', shell=True)
"""    
