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
from settings import genesis, timeout, size, starttps, parameters
from multiprocessing import Process, Pool
import asyncio
import concurrent.futures

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


async def main():
    # Seed the RNG through GnuPG
    rng.seed(check_output(['gpg', '-a', '--gen-random', '1', '32']))
    while int(time()) <= timeout:
        # The input of batchSend() is equivalent to the current TPS. batchSend() should take 1 second to halt, but transactions may still be sending.
        await asyncio.run(batchSend((floor((int(time())-genesis)/3600))+starttps))
        await collect(asyncio.gather(mine()))
    print("The Times 03/Jan/2009 Chancellor on brink of second bailout for banks")

async def batchSend(tps):
    node = []
    for i in parameters.get(tps):
        await asyncio.run(conn(*i))

async def mine():
    if (int(time())-genesis) % 600 == 0:
        nodemine = rng.randint(1,size+1)
        await conn(nodemine,"generatetoaddress",(1,getAddr(nodemine)),0,"Mined by %s\n" % str(nodemine))
        if conn(nodemine,"getblockcount",(),0,"")["result"] - 1323 % 6 == 0:
            return 2
        else:
            return 1
    elif (int(time())-genesis) % 10 == 0:
        return 1
    else:
        return 0

async def noCollect():
    pass

async def twoCollect():
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None,minFee)
    await loop.run_in_executor(None,memPool)

async def threeCollect():
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None,minFee)
    await loop.run_in_executor(None,medFee,((floor((int(time())-genesis)/3600+1))+starttps,))
    await loop.run_in_executor(None,memPool())

async def collect(tocollect):
    loop = asyncio.get_running_loop()
    cSwitch = {
        0: noCollect,
        1: twoCollect,
        2: threeCollect,
    }
    asyncio.run(cSwitch.get(tocollect)())

if __name__ == "__main__":
    asyncio.run(main())