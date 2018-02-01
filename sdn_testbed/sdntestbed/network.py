#!/usr/bin/env python

import time

from mininet.cli import CLI
from mininet.log import setLogLevel, info, error
from mininet.net import Mininet
from mininet.link import Intf
from mininet.link import TCLink
from mininet.topolib import Topo
from mininet.util import quietRun
from mininet.node import RemoteController

from networkx import nx
from random import randint
from termcolor import colored

from controller import Controller

class RandomTopo(Topo):
    "Random topology"

    def __init__(self, graph_file, host_num):
        Topo.__init__(self)
        self.vertex = {}
        self.graph = {}
        
        # Create graph
        self.graph = nx.read_gml(graph_file)

        # Create switches
        for n in self.graph.nodes():
            switch_name = 'sw'+str(n+1)
            switch = self.addSwitch(switch_name, protocols='OpenFlow13', dpid=str(n+1))
            
            self.graph.node[n]['name'] = switch_name
            self.vertex[switch_name] = n
        
        # Create servers
        
        # Create hosts
        for h in range(1, host_num+1):
            host_name = 'h'+str(h)
            switch_name = 'sw'+str(randint(1, self.graph.number_of_nodes()))
            host = self.addHost(host_name, mac="00:00:00:00:00:"+str(h))
            self.addLink(host, switch_name,)#, bw=2
            self.vertex[host_name] = self.vertex[switch_name]

#            for n in self.graph.nodes():
#              switch_name = self.graph.node[n]['name']
#randint(1, self.graph.number_of_nodes())
#              host = self.addHost(host_name, mac="00:00:00:00:00:"+str(h))
#              self.addLink(host, switch_name,)#, bw=2
            
#                self.vertex[host_name] = self.vertex[switch_name]
        
        # Create links between switches
        for e in self.graph.edges():
            link = self.addLink(self.graph.node[e[0]]['name'], self.graph.node[e[1]]['name'])#, bw=2


class Network(Mininet):
    "Random network"
    
#    def __init__(self, controller, network_size, host_num):
    def __init__(self, graph_file, controller, host_num):
        self.host_num = host_num#3*network_size/2

        # Create network
        #setLogLevel('info')
        self.topo = RandomTopo(graph_file, self.host_num)
        Mininet.__init__(self, topo=self.topo, controller=None)#, link=TCLink
        self.addController('c0', controller=RemoteController, ip=controller.ip, port=6653)
    
    def __enter__(self):
        # Start network emulation
        print 'Network: size = host number = '+str(self.host_num)
        self.start()
         
        # Disable IPv6
        for h in self.hosts:
            h.cmd("sysctl -w net.ipv6.conf.all.disable_ipv6=1")
            h.cmd("sysctl -w net.ipv6.conf.default.disable_ipv6=1")
            h.cmd("sysctl -w net.ipv6.conf.lo.disable_ipv6=1")
        
        for sw in self.switches:
            sw.cmd("sysctl -w net.ipv6.conf.all.disable_ipv6=1")
            sw.cmd("sysctl -w net.ipv6.conf.default.disable_ipv6=1")
            sw.cmd("sysctl -w net.ipv6.conf.lo.disable_ipv6=1")        
        
        time.sleep(1)
        #CLI(self)
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        # Stop network emulation
        #print colored('Stop network', 'cyan')
        print 'Stop network'
        self.stop()
    
    def _CLI(self):
        CLI(self)
        
    def topo(self):
        return self.topo
    
    def graph(self):
        return self.topo.graph
    
    def vertex(self, vertex_name):
        return self.topo.vertex[vertex_name]
    
    def edge_connectivity(self):
        return nx.edge_connectivity(self.topo.graph)
