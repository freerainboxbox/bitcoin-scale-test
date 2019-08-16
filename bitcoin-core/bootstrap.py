#!/usr/bin/python3
# Preamble
import random as rng
from nodetools import getIP, getAddr, getPriv, localConn
from os import system
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from settings import size, starttps

'''
This script bootstraps the network.
1. Give each node their vanity private key.
2. Have node 1 mine 1322 blocks.
3. Send 14.8 BTC to every node.

As a bootstrap script, this does not require concurrency.
Pull requests to add concurrency are welcome, but not necessary.

If you are local testing (using multistart.sh),replace every instance
of conn() with localConn() after the preamble, for every file.
'''


def main():
    while True:
        choice = input("Proceed to import keys? [Y/n] ")
        if choice.upper() == "Y":
            for i in range(1, size+1):
                # Import respective private keys to nodes
                conn(i, "importprivkey", (getPriv(i)), 0, "")
                # Set peer list to 0
                # localConnect node to 8 peers
                peers = rng.sample(range(1, size+1), 8)
                ###############################################################################
                # Be sure to comment out the line 37 and uncomment line 38 for local testing! #
                ###############################################################################
                for peer in peers:
                    conn(i, "addnode", (str(getIP(peer))+":8333", 'add'), 0, "")
                    #conn(i, "addnode", ("127.0.0.1:"+str(22000+peer), 'add'), 0, "")
                    print("%s ==> %s" % (str(i), str(peer)))
            print("P2P bootstrapped.")
            break
        elif choice.upper() == "N":
            print("Skipping.")
            break
        else:
            print("Enter 'Y' or 'n'.\n")
    # Mine 1322 blocks to node 1, 1222 blocks of immediately spendable rewards, 14949.99998350 BTC.
    while True:
        choice = input("Proceed to mine 1322 blocks? [Y/n] ")
        if choice.upper() == "Y":
            conn(1, 'generatetoaddress',
                 (1322, 'mooo1TVU7edAhZNiwFAdjNarvgXQXsZYSh'), 0, "")
            print("Mined 1322")
            break
        elif choice.upper() == "N":
            print("Skipped.")
            break
        else:
            print("Enter 'Y' or 'n'.\n")
    # Endow each address with 14.8 BTC.
    # Each transaction has 10 outputs, 100 transactions total.
    while True:
        choice = input("Endown all addresses? [Y/n] ")
        if choice.upper() == "Y":
            for i in range(0, size, 10):
                conn(1, 'sendmany', ("", {getAddr(i+1): 14.8, getAddr(i+2): 14.8, getAddr(i+3): 14.8, getAddr(i+4): 14.8, getAddr(
                    i+5): 14.8, getAddr(i+6): 14.8, getAddr(i+7): 14.8, getAddr(i+8): 14.8, getAddr(i+9): 14.8, getAddr(i+10): 14.8}), 0, "")
            break
        elif choice.upper() == "N":
            print("Skipped.")
            break
        else:
            print("Enter 'Y' or 'n'. \n")
    # Height 1323
    while True:
        choice = input("Proceed to mine #1323? [Y/n] ")
        if choice.upper() == "Y":
            conn(1, 'generatetoaddress',
                 (1, 'mooo1TVU7edAhZNiwFAdjNarvgXQXsZYSh'), 0, "")
            break
        elif choice.upper() == "N":
            print("Skipped.")
            break
        else:
            print("Enter 'Y' or 'n'.\n")


if __name__ == "__main__":
    main()
