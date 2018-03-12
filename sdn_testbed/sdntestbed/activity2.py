
import time
import re
from random import choice
from random import randint
from subprocess import call

MULTICAST_VLAN = 405

class Activity(object):
    def __init__(self): pass
    def start_activity(self): pass
    def stop_activity(self): pass

class UnicastActivity(Activity):
    def __init__(self, controller, network, hosts, host_pairs=None):
        self.controller = controller
        self.network = network
        self.hosts = list(hosts)
        self.host_pairs = {}
        self.host_ip = {}
        self.pids = {}
        self.pid_listen = {}
        
        # Create host pairs
        if host_pairs != None:
            self.host_pairs = host_pairs
        else:
            # Partice hosts by pairs (if host number is odd then discard one host)
            tmp_hosts = self.hosts
            while len(tmp_hosts)>1:
                host1_num = randint(0, len(tmp_hosts)-1)
                host1 = tmp_hosts[host1_num]
                del tmp_hosts[host1_num]
                
                host2_num = randint(0, len(tmp_hosts)-1)
                host2 = tmp_hosts[host2_num]
                del tmp_hosts[host2_num]
                
                self.host_pairs[host1] = host2
        
        # Set host's ip addresses
        for host1 in self.host_pairs:
            if len(host1.intfList())>0:
                host2 = self.host_pairs[host1]
                # Save ip
                host1_ip = host1.intfList()[0].ip
                host2_ip = host2.intfList()[0].ip
                self.host_ip[host1.name] = '10.0.0.'+str(host1.name[1:])
                self.host_ip[host2.name] = '10.0.0.'+str(host2.name[1:])
                print(self.host_ip[host1.name], self.host_ip[host2.name])
            
    def start(self):

        # Start performance test
        port_num = 5200
        for host1 in self.host_pairs:
            host2 = self.host_pairs[host1]

            bandwidth = 1 # Mbit/s
            port_num += 1
            #host1.cmd('sudo tcpdump -i '+host1.name+'-eth0 -U -w azaza.pcap &')

            output = host2.cmd('python communication.py ' + self.host_ip[host2.name] + ' server')
            self.pids[host2] = int(re.findall(r'\d+', output)[0])

            output = host1.cmd('python communication.py ' + self.host_ip[host2.name] + ' client') 
            self.pids[host1] = int(re.findall(r'\d+', output)[0])

            #host2.cmd('xterm -e "iperf3 -s -B '+self.host_ip[host2.name]+' -i 1" &')
            #host1.cmd('xterm -e "iperf3 -c '+self.host_ip[host2.name]+' -u -b '+str(bandwidth*1000000)+' -i 1 -t 60" &')
    
    def stop(self):

        # Kill launched dialogs between hosts by process's pids
        for host in self.pids.keys():
            host.cmd('kill ' + str(self.pids[host]+1))
            self.pids.pop(host)
#        for host in self.hosts: 
#            host.cmd('kill $(jobs -p)')
        
        self.controller.clear_routes()

    def listen(self):

        # Start servers on all hosts (using for duplicate and mitm attacks)
        # We also memorize pids of this launched processes to kill them after
        netcat_port = 5555
        for host1 in self.host_pairs:
            host2 = self.host_pairs[host1]
            output = host1.cmd('python server.py ' + self.host_ip[host1.name] + ' ' + str(netcat_port))
            self.pid_listen[host1] = int(re.findall(r'\d+', output)[0])
            output = host2.cmd('python server.py ' + self.host_ip[host2.name] + ' ' + str(netcat_port))
            self.pid_listen[host2] = int(re.findall(r'\d+', output)[0])
        
    def stop_listen(self):

        # Kill launched servers on hosts
        for host in self.pid_listen.keys():
            host.cmd('kill ' + str(self.pid_listen[host]+1))
            self.pid_listen.pop(host)

