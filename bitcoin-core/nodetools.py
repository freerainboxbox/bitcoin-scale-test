#!/usr/bin/python3
# Preamble
import csv
import multiprocessing
from settings import genesis, timeout
from subprocess import call
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from socket import error as socketerror
from data_collection import minFee, medFee, memPool
from time import time

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

# Class definition of an RPC call thread.
class RPCall (multiprocessing.Process):
    def __init__(self, reqnum, node, method, args, extra):
        # Request number within a second (from 1 to TPS interval)
        self.reqnum = int(reqnum)
        # Node Identifier
        self.node = int(node)
        # JSON-RPC Method
        self.method = str(method)
        # JSON-RPC Method arguments
        self.args = tuple(args)
        # Extra string to print at end
        self.extra = extra
        # If request number is 0,
        # the request is a generatetoaddress call.
        assert 0 <= self.reqnum <= 120
        assert 1 <= self.node <= 120
    def run(self):
        try:
            # TODO: Add logic for sending calls.
            conn(self.node).self.method(self.args)
            print(self.extra)
            # Exit with 0, no exception (Not in use yet)
            return(self.node,self.method,self.args,0,None)
        except (JSONRPCException, socketerror) as e:
            # Exit with 1 with exception body (Not in use yet)
            return(self.node,self.method,self.args,1,str(e))

# Class definition of a combined data collector thread.
class DataCollector (multiprocessing.Process):
    def __init__(self, dependent, tps):
        self.dependent=int(dependent)
        self.tps=int(tps)
        assert 1<=self.dependent<=3
        assert 1<=self.tps<=120
    def run(self):
        if self.dependent == 1:
            AtomMinFee = open("AtomMinFee.csv", "a")
            AtomMinFee.write("%s,%s,AtomMinFee" % (str(int(time())-genesis),str(minFee())))
            AtomMinFee.close()
        elif self.dependent == 2:
            AtomMedFee = open("AtomMedFee.csv", "a")
            AtomMedFee.write("%s,%s,AtomMedFee" % (str(self.tps),str(medFee(self.tps))))
            AtomMedFee.close()
        elif self.dependent == 3:
            MemPool = open("MemPool.csv", "a")
            MemPool.write("%s,%s,MemPool"% (str(int(time())-genesis),str(memPool())))
            MemPool.close()
