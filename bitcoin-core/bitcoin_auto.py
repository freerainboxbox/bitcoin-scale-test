#!/usr/bin/python3
# Preamble
from nodetools import getIP, getAddr, conn, localConn, tps, Pi
from data_collection import minFee, medFee, memPool
# from os import system
import random as rng
from subprocess import check_output
from time import time, sleep
from math import floor
from data_collection import minFee, medFee, memPool
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from settings import genesis, timeout, size, starttps, timeout, parameters
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
    while int(time()) <= timeout:
        # The input of batchSend() is equivalent to the current TPS. batchSend() should take 1 second to halt, but transactions may still be sending.
        batchSend(tps())
        tocollect = mine()
        collect(tocollect)
    print("The Times 03/Jan/2009 Chancellor on brink of second bailout for banks")

# pi is the offset from the start of the tps period as an integer. It ranges from 1 to 3600.
# The formula for the transaction index within a TPS period is Pi*tps. The end of the range is (Pi+1)*tps

def txnListGen(tps=tps()):
    pi = Pi()
    period = parameters.get(str(tps))
    return period[(pi-1)*tps:pi*tps]

def batchSend(tps):
    txns = Pool(processes=tps)
    node = []
    second = txnListGen()
    txns.starmap_async(localConn,second)

def mine():
    if ((int(time())-genesis) % 600 == 0 and int(time()) != genesis):
        nodemine = rng.randint(1,size)
        generate = Process(target=localConn, args=(nodemine,"generatetoaddress",(1,getAddr(nodemine)),0,"Mined by %s\n" % str(nodemine)))
        generate.start()
        generate.join()
        if localConn(nodemine,"getblockcount",(),0,"") - 1323 % 6 == 0:
            return 2
        else:
            return 1
    elif (int(time())-genesis) % 10 == 0:
        return 1
    else:
        return 0

# Collect nothing.
def noCollect():
    pass

# Collect MinFee (1) and MemPool (3)
def twoCollect():
    processes = []
    processes.append(Process(target=minFee))
    processes.append(Process(target=memPool))
    for process in processes:
        process.start()

# Collect MinFee (1) MedFee(2) and MemPool (3)
def threeCollect():
    processes = []
    processes.append(Process(target=minFee))
    processes.append(Process(target=medFee, args=((floor((int(time())-genesis)/3600+1))+starttps)))
    processes.append(Process(target=memPool))
    for process in processes:
        process.start()

cSwitch = {
    0 : noCollect,
    1 : twoCollect,
    2 : threeCollect
}

def collect(tocollect):
    cSwitch.get(tocollect)()

if __name__ == "__main__":
    main()