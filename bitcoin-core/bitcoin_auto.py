#!/usr/bin/python3
# Preamble
from nodetools import getIP, getAddr, conn, RPCall, DataCollector
# from os import system
import random as rng
from subprocess import check_output
from time import time, sleep
from math import floor
from data_collection import minFee, medFee, memPool
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException

'''
This script automates data collection and transaction gossip.
Network must be bootstrapped first, see bootstrap.py.

There are a total of ~26136000 transactions in this experiment of 5 days with 120 TPS periods.
720 blocks will be mined on top of the 1323 initial reward generation, yielding 2043 blocks.

Use jgarzik/python-bitcoinrpc for making JSON-RPC calls.

1 Bitcoin (BTC) = 10^8 Satoshis
3600 seconds = 1 hour (TPS interval)
600 seconds = 10 minutes (Time between blocks)
432000 seconds = 5 days (Experiment length)

This version requires the command node to be large enough to handle
120 RPC requests per second, plus dependent variable I/O.
'''
# BUG: Need to parallelize processes. Not suitable for further experimentation until fixed.

def main():
    # Seed the RNG through GnuPG
    rng.seed(check_output(['gpg', '-a', '--gen-random', '1', '32']))
    while int(time()) <= timeout:
        # The input of batchSend() is equivalent to the current TPS. batchSend() should take 1 second to halt, but transactions may still be sending.
        batchSend((floor((int(time())-genesis)/3600+1)))
        mine()
    print("The Times 03/Jan/2009 Chancellor on brink of second bailout for banks")

# Originally called query()
def batchSend(tps):
    txns = {}
    node = {}
    for i in range(1,tps+1):
        # Generate node IDs
        node[i] = rng.sample(range(1,1001),2)
        # Query node[i][0] to send 1 satoshi (new dust limit) to node[i][1]
        #conn(nodes[0]).sendtoaddress(getAddr(nodes[1]), 0.00000001)
        #return (str(nodes[0]), str(nodes[1]))
    for i in range(1,tps+1):
        txns[i] = RPCall(i, node[i][0], "sendtoaddress", (getAddr(node[i][1]),0.00000001),"From %s to %s" % (node[i][0],node[i][1]))
    for i in range(1,tps+1):
        txns[i].start()
        sleep(1/tps)


def mine():
    if (int(time())-genesis) % 600 == 0:
        nodemine = rng.randint(1,1001)
        RPCall(0,nodemine,"generatetoaddress",getAddr(nodemine),"Mined by %s" % str(nodemine))

# The following are booleans, not the functions from data_collection.
def collect(minfee,medfee,mempool):
    pass
    # TODO: Add collector


if __name__ == "__main__":
    # Set local experiment start time as Epoch
    genesis = int(time())
    # Set end time as Epoch
    timeout = genesis+432000
    main()