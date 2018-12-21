#!/usr/bin/python3
# Preamble
from nodetools import getIP, getAddr, getPriv, conn
from os import system
import random as rng

'''
This script bootstraps the network.
1. Give each node their vanity private key.
2. Have node 1 mine 200000 blocks.
3. Send 9800 BTC to every node.
'''


def main():
    existconn = []
    for i in range(1, 1001):
        # Import respective private keys to nodes
        conn(i).importprivkey(getPriv(i))
        # Connect node to 8 peers
        for j in range(0, 8):
            match = True
            while match:
                peer = rng.randint(1, 1000)
                if peer != i and (peer in existconn == False):
                    existconn.append(peer)
                    existconn.append(i)
                    match = False
                    conn(i).addnode(getIP(
                        peer)+':8333', 'add')
                    print("%s ==> %s" % (str(i), str(peer)))
            conn(i).addnode(getIP(randint(1,1000))+':8333', 'add')
    # Mine 200000 blocks to node 1, 199900 blocks of immediately spendable rewards, 9995000 BTC.
    for i in range(1, 2001):
        conn(1).generatetoaddress(
            100, 'mooo1TVU7edAhZNiwFAdjNarvgXQXsZYSh')
        print("Block %s00" % i)
    # Endow each address with 9800 BTC.
    # Each transaction has 10 outputs, 100 transactions total.
    for i in range(0, 1000, 10):
        conn(1).sendmany("", {getAddr(i+1): 9800, getAddr(i+2): 9800, getAddr(i+3): 9800, getAddr(i+4): 9800, getAddr(
            i+5): 9800, getAddr(i+6): 9800, getAddr(i+7): 9800, getAddr(i+8): 9800, getAddr(i+9): 9800, getAddr(i+10): 9800})


if __name__ == "__main__":
    main()

