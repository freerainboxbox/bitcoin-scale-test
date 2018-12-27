#!/usr/bin/python3
# Preamble
import random as rng
from nodetools import getIP, getAddr, getPriv, conn
from os import system
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException

'''
This script bootstraps the network.
1. Give each node their vanity private key.
2. Have node 1 mine 1322 blocks.
3. Send 14.8 BTC to every node.
'''


def main():
    for i in range(1, 1001):
        # Import respective private keys to nodes
        conn(i).importprivkey(getPriv(i))
        # Set peer list to 0
        # Connect node to 8 peers
        peers = rng.sample(range(1,1001),8)
        for peer in peers:
            conn(i).addnode(getIP(peer)+':8333','add')
            print("%s ==> %s" % (str(i), str(peer)))
    # Mine 1322 blocks to node 1, 1222 blocks of immediately spendable rewards, 14949.99998350 BTC.
    # Comment out next 4 lines if on pregen image
    conn(1).generatetoaddress(
        1322, 'mooo1TVU7edAhZNiwFAdjNarvgXQXsZYSh')
    print("Mined 1322")
    # Endow each address with 14.8 BTC.
    # Each transaction has 10 outputs, 100 transactions total.
    for i in range(0, 1000, 10):
        conn(1).sendmany("", {getAddr(i+1): 14.8, getAddr(i+2): 14.8, getAddr(i+3): 14.8, getAddr(i+4): 14.8, getAddr(
            i+5): 14.8, getAddr(i+6): 14.8, getAddr(i+7): 14.8, getAddr(i+8): 14.8, getAddr(i+9): 14.8, getAddr(i+10): 14.8})
    conn(1).generatetoaddress(
            1, 'mooo1TVU7edAhZNiwFAdjNarvgXQXsZYSh')


if __name__ == "__main__":
    main()