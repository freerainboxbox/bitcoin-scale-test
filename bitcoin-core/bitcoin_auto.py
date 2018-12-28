#!/usr/bin/python3
# Preamble
from nodetools import getIP, getAddr, conn
# from os import system
import random as rng
from subprocess import check_output
from time import time, sleep
from math import floor
from data_collection import minFee, medFee, memPool

'''
This script automates data collection and transaction gossip.
Network must be bootstrapped first, see bootstrap.py.

There are a total of ~156816000 transactions in this experiment of 5 days with 120 TPS periods.
720 blocks will be mined on top of the 1323 initial reward generation, yielding 2043 blocks.

Use jgarzik/python-bitcoinrpc for making JSON-RPC calls.

1 Bitcoin (BTC) = 10^8 Satoshis
3600 seconds = 1 hour (TPS interval)
600 seconds = 10 minutes (Time between blocks)
432000 seconds = 5 days (Experiment length)

This version requires the command node to be large enough to handle
120 RPC requests per second, plus dependent variable I/O.
'''

def main():
    # Seed the RNG through GnuPG
    rng.seed(check_output(['gpg', '-a', '--gen-random', '1', '32']))
    # Set local experiment start time as Epoch
    genesis = int(time())
    # Set end time as Epoch
    timeout = genesis+432000
    while int(time()) <= timeout:
        # The input of query() is equivalent to the current TPS.
        nodeboth = query((floor((int(time())-genesis)/3600+1)))
        print("From %s to %s" % nodeboth)
        # 600 seconds is the block time, mine if 600 seconds have passed.
        if (int(time())-genesis) % 600 == 0:
            # Mine 1 block, store miner ID
            nodemine = mine()
            print("Mined by %s" % str(nodemine))
            sleep(1)
            # Query miner node what the block count is, check if a multiple of 6
            if (conn(nodemine).getblockchaininfo()["blocks"]) - 200001 % 6 == 0:
                # Get median fee of previous completed TPS interval
                AtomMedFee = open("AtomMedFee.csv", "a")
                AtomMinFee = open("AtomMinFee.csv", "a")
                MemPool = open("MemPool.csv", "a")
                AtomMedFee.write("%s,%s,bitcoin-mini\n" % (int(time()-genesis),
                                                           medFee(floor((int(time()-genesis)/3600)-1))))
                AtomMinFee.write("%s,%s,bitcoin-mini\n" %
                                 (int(time()-genesis), minFee()))
                MemPool.write("%s,%s,bitcoin-mini\n" %
                              (int(time()-genesis), memPool()))
                AtomMedFee.close()
                AtomMinFee.close()
                MemPool.close()
            else:
                # Skip median fee
                AtomMinFee = open("AtomMinFee.csv", "a")
                MemPool = open("MemPool.csv", "a")
                AtomMinFee.write("%s,%s,bitcoin-mini\n" %
                                 (int(time()-genesis), minFee()))
                MemPool.write("%s,%s,bitcoin-mini\n" %
                              (int(time()-genesis), memPool()))
                AtomMinFee.close()
                MemPool.close()
        elif (int(time())-genesis) % 10 == 0:
            # Skip median fee
            AtomMinFee = open("AtomMinFee.csv", "a")
            MemPool = open("MemPool.csv", "a")
            AtomMinFee.write("%s,%s,bitcoin-mini\n" %
                             (int(time()-genesis), minFee()))
            MemPool.write("%s,%s,bitcoin-mini\n" %
                          (int(time()-genesis), memPool()))
            AtomMinFee.close()
            MemPool.close()
        #If not a multiple of 10 or 600 seconds, skip and query again.


def query(tps):
    match = True
    while match:
        # Generate node IDs
        nodesend = rng.randint(1, 1000)
        noderecv = rng.randint(1, 1000)
        if nodesend != noderecv:
            match = False
            print(tps)
            # Wait for the inverse of TPS period, or tps^-1
            sleep(1/tps)
            # Query nodesend to send 1 satoshi (new dust limit) to noderecv
            conn(nodesend).sendtoaddress(getAddr(noderecv), 0.00000001)
            return (str(nodesend), str(noderecv))


def mine():
    nodemine = rng.randint(1, 1000)
    conn(nodemine).generatetoaddress(1,getAddr(nodemine))
    return nodemine


if __name__ == "__main__":
    main()