
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
        
        # Set routes
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
        #call("rm ../.tmp/*.pcap > /dev/null 2>&1", shell=True)
        port_num = 5200
        netcat_port = 5555
        for host1 in self.host_pairs:
            host2 = self.host_pairs[host1]

            bandwidth = 1 # Mbit/s
            port_num += 1
            #host1.cmd('sudo tcpdump -i '+host1.name+'-eth0 -U -w azaza.pcap &')

            output = host2.cmd('python communication.py ' + self.host_ip[host2.name] + ' server')
            self.pids[host2] = [int(re.findall(r'\d+', output)[0])]

            output = host1.cmd('python communication.py ' + self.host_ip[host2.name] + ' client') 
            self.pids[host1] = [int(re.findall(r'\d+', output)[0])]

            output = host1.cmd('python server.py ' + self.host_ip[host1.name] + ' ' + str(netcat_port))
            self.pids[host1].append(int(re.findall(r'\d+', output)[0]))
            output = host2.cmd('python server.py ' + self.host_ip[host2.name] + ' ' + str(netcat_port))
            self.pids[host2].append(int(re.findall(r'\d+', output)[0]))
            #host2.cmd('xterm -e "iperf3 -s -B '+self.host_ip[host2.name]+' -i 1" &')
            #host1.cmd('xterm -e "iperf3 -c '+self.host_ip[host2.name]+' -u -b '+str(bandwidth*1000000)+' -i 1 -t 60" &')
    
    def stop(self):
        for host in self.pids.keys():
            for pid in self.pids[host]:
              host.cmd('kill ' + str(pid+1))
            self.pids.pop(host)
#        for host in self.hosts: 
#            host.cmd('kill $(jobs -p)')
        
        self.controller.clear_routes()

'''    
                # Create route by controller
                sw1 = host1.intfList()[0].link.intf2.node
                dpid1 = sw1.dpid
                port1 = self.network.topo.port(host1.name, sw1.name)[1]
                
                sw2 = host2.intfList()[0].link.intf2.node
                dpid2 = sw2.dpid
                port2 = self.network.topo.port(host2.name, sw2.name)[1]
    
                self.controller.set_route(dpid1, port1, dpid2, port2, vlan)
                #print "host_pairs["+host1.name+"] = "+host2.name
                #print "set_route("+dpid1.lstrip("0")+":"+str(port1)+" <-> "+dpid2.lstrip("0")+":"+str(port2)+", vlan="+str(vlan)            
'''                
'''    
                # Set vlan
                host1.cmd('/sbin/vconfig add '+host1.name+'-eth0 '+str(vlan))
                host1.cmd('ifconfig '+host1.name+'-eth0.'+str(vlan)+' '+self.host_ip[host1.name]+' netmask 255.255.255.0')
                host1.cmd('ifconfig '+host1.name+'-eth0 '+host1_ip+' netmask 255.255.255.0')
                #host1.cmd('route add -net 10.0.1.0/24 '+host1.name+'-eth0.'+str(vlan))
                
                host2.cmd('/sbin/vconfig add '+host2.name+'-eth0 '+str(vlan))
                host2.cmd('ifconfig '+host2.name+'-eth0.'+str(vlan)+' '+self.host_ip[host2.name]+' netmask 255.255.255.0')
                host2.cmd('ifconfig '+host2.name+'-eth0 '+host2_ip+' netmask 255.255.255.0')
                #host2.cmd('route add -net 10.0.1.0/24 '+host2.name+'-eth0.'+str(vlan))
'''                
