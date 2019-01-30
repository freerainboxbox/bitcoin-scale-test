#/usr/bin/python3
# Start and end times for import.
from time import time
from nodetools import getIP
from web3 import Web3,personal,admin,HTTPProvider
# Set local experiment start time as Epoch
genesis = int(time())
# Set end time as Epoch
timeout = genesis+432000
# Reverse search dictionary from IP to node #
enode = {}
for i in (1,1001):
    enode[i]=Web3(HTTPProvider("http://"+getIP(i))).admin.nodeInfo['enode']