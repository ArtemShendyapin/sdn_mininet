import re
import random

class Attack:
  victim_mac = ''
  victim_rec_mac = ''
  phase = 0
  atk_type = ''
  atk_switch = None
  atk_host = None
  mode = ''
  feedback = ''

  def __init__(self, victim_mac, victim_rec_mac, phase, atk_type, atk_host, host_list=None):
    self.victim_mac = victim_mac
    self.victim_rec_mac = victim_rec_mac
    self.phase = phase
    self.atk_type = atk_type
    self.atk_host = atk_host
    self.host_list = host_list

  def choose_switch(self, atk_switch_list):
    pot_list = []
    for switch in atk_switch_list:
      flows = switch.cmd("ovs-ofctl -O OpenFlow13 dump-flows " + str(switch.name), shell=True)
      flow_list = flows.split('\n')
      for flow in flow_list:
        if self.victim_rec_mac == 'any':
          check_elem = re.findall(r'dl_src='+str(self.victim_mac), flow)
        else:
          check_elem = re.findall(r'dl_src='+str(self.victim_mac)+'.*dl_dst='+str(self.victim_rec_mac), flow)
        if check_elem:
#          print("Found on switch: " + str(switch.name))
#          print(check_elem)
        # If list is not empty, then we found rule on current switch
        # We need to add this switch to list of potential attack switches
          pot_list.append(switch)
          break

    if pot_list:
    # If list of potential attacks is not empty, then we can use mod-flow option
    # We need to choose one of switches in list as an attack switch
      self.atk_switch = random.choice(pot_list)
      self.mode = 'mod-flows'
    else:
    # Else we need to choose one switch and use add-flow option
      self.atk_switch = random.choice(atk_switch_list)
      self.mode = 'add-flow'
    print(self.mode)

  def print_information(self):
    print("Phase: " + str(self.phase))
    print("Attack type: " + self.atk_type)
    print("Attack switch: " + self.atk_switch.name)
    print("Victim mac: " + self.victim_mac)
    print("Victim rec mac: " + self.victim_rec_mac)
    print("Established rule:")
    search_for = r''
    search_flow = self.feedback.split('\n')
    search_elems = search_flow[-2].split(' ')
    for search_elem in search_elems:
      search_for += search_elem + '.*'

    flows = self.atk_switch.cmd("ovs-ofctl -O OpenFlow13 dump-flows " + str(self.atk_switch.name), shell=True)
    flow_list = flows.split('\n')
    for flow in flow_list:
      check_elem = re.findall(search_for, flow)
#      check_elem = re.findall(r'dl_src='+str(self.victim_mac)+'.*dl_dst='+str(self.victim_rec_mac), flow)
      if check_elem:
        print(flow)
        break
    print('\n')


class TestCase:
  attacks = []
  av_switches = []

  def __init__(self, attacks, av_switches):
    self.attacks = attacks
    self.av_switches = av_switches
#    self.comp_sw = []

  def start_attacks(self, phase):
    for attack in self.attacks:
       if attack.phase == phase:
         attack.choose_switch(self.av_switches)
         command = "python ../attacker/attacker.py "+attack.atk_type+" "+attack.atk_switch.name+" "+attack.mode+" "+attack.victim_mac+" "+attack.victim_rec_mac
         if attack.atk_type == "duplicate":
           addresses = ""
           for host in attack.host_list:
             if host.name != attack.atk_host.name:
               addresses += host.name
           command += " "+addresses
         attack.feedback = attack.atk_host.cmd(command)
#       attack_sw = choice(self.av_switches)
#       attack_sw.cmd(attack)
#       self.comp_sw.append(attack_sw)

  def stop_attacks(self):
    for attack in self.attacks:
      attack.print_information()
#    for switch in self.comp_sw:
#      switch.cmd('kill &(jobs -p)')
