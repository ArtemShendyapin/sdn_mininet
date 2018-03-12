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

    # These are names of bound switches, to which will be connected hosts
    # Other switches will be treated as unbounded and potentially compromised
#    bound_sw = ['sw1', 'sw4', 'sw9', 'sw10', 'sw10', 'sw17', 'sw28', 'sw30']
    bound_sw = ['sw1', 'sw4', 'sw6', 'sw7']
    unbound_names = []
    with Network('../GtsPoland.gml', controller_list, bound_sw, unbound_names) as network:
        unbound_sw = []
        for name in unbound_names:
          unbound_sw.append(network.getNodeByName(name))

        # For each bound switch we create host
        host_list = [network.getNodeByName('h' + str(i)) for i in range(1, len(bound_sw) + 1)]
        test = UnicastActivity(controller_list, network, host_list)

        # Then we choose host, that would run attacks, and set the list of 
        # attacks
        # Attack parameters: 1) dl_dst of flow; 
        #                    2) dl_src of flow (could be set as 'any');
        #                    3) Number of phase, when attack should be run;
        #                    4) Attack type;
        #                    5) Attack host;
        #                    6) List of hosts with launched server (for 
        # complicated attacks)
        atk_host = network.getNodeByName('h4')
        # Don't forget not to attack yours attack host mac address :)
        attacks = [
      Attack('00:00:00:00:00:01', 'any', 2, 'duplicate', atk_host, host_list),
      Attack('00:00:00:00:00:02', 
             '00:00:00:00:00:03', 2, 'MitM', atk_host, host_list),
#      Attack('00:00:00:00:00:01', 'any', 2, 'flood', atk_host),
#      Attack('00:00:00:00:00:02', 'any', 2, 'drop', atk_host),
#           Attack('00:00:00:00:00:03', 'any', 2, 'flood'),
      Attack('00:00:00:00:00:03', 'any', 1, 'incorrect_forwarding', atk_host),
#           Attack('00:00:00:00:00:07', 'any', 3, 'drop'),
          ]
 
        attacker = TestCase(attacks, unbound_sw, network)
        # Set number of phases
        phase_num = 4
        for phase in range(phase_num):

          # Launch hosts comunications and listening servers on them
          test.start()
          if phase == 0:
            test.listen()
          attacker.start_attacks(phase)
          # Wait while phase will end
          sleep(25)
          test.stop()

          # Using for particing hosts into pairs by another way for next phase
          test.__init__(controller_list, network, host_list)
        # Stop servers on hosts and print information about attacks
        attacker.stop_attacks()
        network._CLI()
        test.stop_listen()
