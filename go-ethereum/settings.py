#/usr/bin/python3
# Start and end times for import.
from time import time
from nodetools import getIP, conn
# Set local experiment start time as Epoch
genesis = int(time())
# Set end time as Epoch
timeout = genesis+432000
# Reverse search dictionary from IP to node #
enode = {}
for i in (1,1001):
    enode[i]=conn(i).admin.nodeInfo['enode']