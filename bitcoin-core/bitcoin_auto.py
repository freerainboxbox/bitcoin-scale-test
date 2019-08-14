#!/usr/bin/python3
# Preamble
from nodetools import getIP, getAddr, conn, localConn
from data_collection import minFee, medFee, memPool
# from os import system
import random as rng
from subprocess import check_output
from time import time, sleep
from math import floor
from data_collection import minFee, medFee, memPool
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from settings import genesis, timeout, size, starttps
from multiprocessing import Process, Pool

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


def main():
    # Seed the RNG through GnuPG
    rng.seed(check_output(['gpg', '-a', '--gen-random', '1', '32']))
    while int(time()) <= timeout:
        # The input of batchSend() is equivalent to the current TPS. batchSend() should take 1 second to halt, but transactions may still be sending.
        batchSend((floor((int(time())-genesis)/3600+1)))
        tocollect = mine()
        collect(tocollect)
    print("The Times 03/Jan/2009 Chancellor on brink of second bailout for banks")

def batchSend(tps):
    txns = Pool(processes=tps)
    node = []
    parameters = []
    for i in range(1,tps+1):
        # Generate node IDs
        node[i] = rng.sample(range(1,size),2)
        # Build parameters list for pool object
        parameters.append((node[i][0],"sendtoaddress",(getAddr(node[i][1]),0.00000001),i/tps,"From %s to %s\n" % (node[i][0],node[i][1])))
    txns.map(conn, parameters)


def mine():
    if (int(time())-genesis) % 600 == 0:
        nodemine = rng.randint(1,size+1)
        generate = Process(target=conn, args=(nodemine,"generatetoaddress",(1,getAddr(nodemine)),0,"Mined by %s\n" % str(nodemine)))
        generate.start()
        generate.join()
        if conn(nodemine,"getblockcount",(),0,"")["result"] - 1323 % 6 == 0:
            return 2
        else:
            return 1
    elif (int(time())-genesis) % 10 == 0:
        return 1
    else:
        return 0

def collect(tocollect):
    processes = []
    if tocollect == 0:
        # Collect nothing.
        start = False
    elif tocollect == 1:
        # Collect MinFee (1) and MemPool (3)
        #processes.append(DataCollector(1,floor((int(time())-genesis)/3600+1)))
        processes.append(Process(target=minFee))
        processes.append(Process(target=memPool))
        start = True
    elif tocollect == 2:
        # Collect MinFee (1) MedFee(2) and MemPool (3)
        processes.append(Process(target=minFee))
        processes.append(Process(target=medFee, args=((floor((int(time())-genesis)/3600+1)))))
        processes.append(Process(target=memPool))
        start = True
    if start:
        # Start all processes
        for process in processes:
            process.start()
    
if __name__ == "__main__":
    main()