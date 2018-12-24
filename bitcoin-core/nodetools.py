#!/usr/bin/python3
# Preamble
import csv
from subprocess import call
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException

# These are some functions used for getting data about nodes themselves.


def getIP(node):
    # Generate IP to query from subnet 10.142.0.0/20 (1000 IPs)
    if node != None:
        # From 10.142.0.2 to 10.142.0.255
        if 1 <= node <= 254:
            nodeip = "10.142.0."+str(1+node)
        # From 10.142.1.0 to 10.142.1.255
        elif 255 <= node <= 510:
            nodeip = "10.142.1."+str(node-255)
        # From 10.142.2.0 to 10.142.2.255
        elif 511 <= node <= 766:
            nodeip = "10.142.2."+str(node-511)
        # From 10.142.3.0 to 10.142.3.171
        elif 767 <= node <= 938:
            nodeip = "10.142.3."+str(node-767)
        # From 10.142.15.192 to 10.142.15.253
        elif 939 <= node <= 1000:
            nodeip = "10.142.15."+str(node-747)
        else:
            print("node is out of range.")
        return nodeip


def getAddr(node):
    # Retrieve address from vanity CSV store
    with open("addresses.csv") as addresses:
        addrlist = list(csv.reader(addresses))
        return addrlist[node][1]


def getPriv(node):
    # Retrieve private key from vanity CSV store
    with open("addresses.csv") as addresses:
        addrlist = list(csv.reader(addresses))
        return addrlist[node][2]


def conn(node):
    # Set python-bitcoinrpc credentials
    return AuthServiceProxy("http://"+"test:test@"+getIP(node)+":8332")