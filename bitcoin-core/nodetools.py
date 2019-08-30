#!/usr/bin/python3
# Preamble
import csv
from settings import genesis, timeout, starttps, size
from subprocess import call
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from socket import error as socketerror
from time import time, sleep
from math import floor
from random import randint as rint

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


def conn(node, method, args, delay, debug):
    # Set python-bitcoinrpc credentials
    #All data collectors will have 0 delay.
    sleep(delay)
    print(debug, end="")
    if type(args) is str:
        proxy = 'AuthServiceProxy("http://test:test@%s:8332").%s%s' % (getIP(node),method,tuple[args])
    elif type(args) is tuple:
        proxy = 'AuthServiceProxy("http://test:test@%s:8332").%s%s' % (getIP(node),method,args)
    else:
        proxy = 'AuthServiceProxy("http://test:test@%s:8332").%s%s' % (getIP(node),method,tuple(args))
    return eval(proxy)


def localConn(node, method, args, delay, debug):
    #For local testing, all JSON-RPC listener ports are node+23000.
    sleep(delay)
    print(debug, end="")
    if type(args) is str:
        proxy = 'AuthServiceProxy("http://user:pw@127.0.0.1:%s").%s%s' % (node+23000,method,tuple([args]))
    elif type(args) is tuple:
        proxy = 'AuthServiceProxy("http://user:pw@127.0.0.1:%s").%s%s' % (node+23000,method,args)
    else:
        proxy = 'AuthServiceProxy("http://user:pw@127.0.0.1:%s").%s%s' % (node+23000,method,tuple(args))
    return eval(proxy)

def tps():
    return (floor((int(time())-genesis)/3600))+starttps

def Pi():
    print("%s-%s-%s" % (int(time()),genesis,(tps()-1)*3600))
    return int(time())-genesis-(tps()-1)*3600