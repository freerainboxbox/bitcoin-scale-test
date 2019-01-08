#!/usr/bin/python3
# Preamble
from nodetools import getIP, getAddr, conn
# from os import system
import random as rng
from subprocess import check_output
from time import time, sleep
from math import floor
from data_collection import minFee, medFee, memPool
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
import socket

'''
This script automates data collection and transaction gossip.
Network must be bootstrapped first, see bootstrap.py.

There are a total of ~156816000 transactions in this experiment of 5 days with 120 TPS periods.
2880 blocks will be mined on top of the 1323 initial reward generation, yielding 4203 blocks.

Use jgarzik/python-bitcoinrpc for making JSON-RPC calls. 

1 Litecoin (LTC) = 10^8 litoshis
900 seconds = 15 minutes (TPS interval)
150 seconds = 2.5 minutes (Time between blocks)
108000 seconds = 1.25 days (Experiment length)

This version requires the command node to be large enough to handle
120 RPC requests per second, plus dependent variable I/O.

Most syntax here is compatible with bitcoind, there are only slight modifications from bitcoin_auto.py
Like Bitcoin, Litecoin has a regtest subsidy halving of 150 blocks.
'''
# BUG: Need to parallelize processes. Not suitable for further experimentation until fixed.

def main():
    # Seed the RNG through GnuPG
    rng.seed(check_output(['gpg', '-a', '--gen-random', '1', '32']))
    # Set local experiment start time as Epoch
    genesis = int(time())
    # Set end time as Epoch
    timeout = genesis+108000
    while int(time()) <= timeout:
        # The input of query() is equivalent to the current TPS.
        try:
            nodeboth = query((floor((int(time())-genesis)/900+1)))
            print("From %s to %s" % nodeboth)
        except socket.error:
            print("Node %s is having trouble sending to node %s, skipping." % (nodeboth[0],nodeboth[1]))
            pass
        # 150 seconds is the block time, mine if 150 seconds have passed.
        if (int(time())-genesis) % 150 == 0:
            # Mine 1 block, store miner ID
            nodemine = mine()
            print("Mined by %s" % str(nodemine))
            sleep(1)
            # Query miner node what the block count is, check if a multiple of 6
            if (conn(nodemine).getblockchaininfo()["blocks"]) - 1323 % 6 == 0:
                # Get median fee of previous completed TPS interval
                AtomMedFee = open("AtomMedFee.csv", "a")
                AtomMinFee = open("AtomMinFee.csv", "a")
                MemPool = open("MemPool.csv", "a")
                AtomMedFee.write("%s,%s,bitcoin-mini\n" % (int(time()-genesis),
                                                           medFee(floor((int(time()-genesis)/900)-1))))
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
        #If not a multiple of 10 or 150 seconds, skip and query again.


def query(tps):
    # Generate node IDs
    nodes = rng.sample(range(1,1001),2)
    print(tps)
    # Wait for the inverse of TPS period, or tps^-1
    sleep(1/tps)
    # Query nodes[0] to send 1 litoshi (new dust limit) to nodes[1]
    try:
        conn(nodes[0]).sendtoaddress(getAddr(nodes[1]), 0.00000001)
        return (str(nodes[0]), str(nodes[1]))
    except JSONRPCException:
        print("%s does not have enough funds to send to %s." % (str(nodes[0]), str(nodes[1])))


def mine():
    while True:
        nodemine = rng.randint(1, 1000)
        try:
            conn(nodemine).generatetoaddress(1,getAddr(nodemine))
            return nodemine
        except socket.error:
            print("Node %s did not respond to mining request. Changing miner..." % nodemine)
            pass


if __name__ == "__main__":
    main()