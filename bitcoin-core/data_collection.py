#!/usr/bin/python3
# Preamble
from subprocess import check_output
from statistics import median
from math import floor
from time import time
from bitcoinrpc.authproxy import AuthServiceProxy,JSONRPCException
import random as rng
import socket

'''
These functions collect the dependent variables (DVs).
They are:
Atomic Minimum Fee (AtomMinFee)
Atomic Median Fee (AtomMedFee)
Unconfirmed Transaction Pool Size (MemPool)
'''

# Must be included to prevent cyclic import.
def conn(node):
    # Set python-bitcoinrpc credentials
    return AuthServiceProxy("http://"+"test:test@"+getIP(node)+":8332")

# Must be included to prevent cyclic import.
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

# AtomMinFee estimator
# Likely will not return any data until the mempool size can stay large enough for the fee estimator to work.
def minFee():
    rawfee = []
    fee = []
    # Get fee for all nodes (maximum wait time is 1008 blocks)
    for i in range(1, 1001):
        try:
            rawfee.append(conn(i).estimatesmartfee(1008))
        except socket.error:
            print("Trouble getting minfee from node %s, skipping." % str(i))
    for i in range(0, 1000):
        try:
            # When the mempool isn't large enough
            if rawfee[i]["errors"] == ['Insufficient data or no feerate found']:
                pass
            else:
                # get fee list
                for j in range(0, 1000):
                    fee.append(rawfee[j]['feerate'] * 100000000)
                # output median of fee list in satoshis
                return int(median(fee))
        except:
            # Occasionally, there will be a KeyError. If so, return None.
            pass


'''
AtomMedFee estimator
Bitcoin JSON-RPC API provides no straightforward way to get transaction fees.
By getting transactions' total input and output, the fees can be calculated by finding the difference.
'''
def medFee(tps):
    # TPS interval start block height
    startht = tps * 6 + 1323
    # Get data from 3 nodes
    while True:
        nodes = rng.sample(range(1,1001),3)
        for i in nodes:
            feelist = []
            # Serialized block with txhashes
            rawblock = []
            # List of txhashes
            txlist = []
            # List of inputs/outputs
            vins = []
            vouts = []
            # Method of escaping faulty requests
            badnode = 0
            for j in range(startht, startht + 7):
                # Get serialized block
                while True:
                    try:
                        # Modulo 1000 to prevent node selection out of range.
                        rawblock = conn((i + badnode) % 1000).getblock(conn((i + badnode) % 1000).getblockhash(j))
                        break
                    except socket.error:
                        print("Problem getting block from %s, retrying." % str((i + badnode) % 1000))
                        badnode += 1
                # Get transaction hash list
                txlist = rawblock["tx"]
                for txhash in txlist:
                    # Coinbase error flag
                    skipflag = True
                    # Input/output values
                    invals = []
                    outvals = []
                    while True:
                        # Get raw transaction
                        try:
                            tx = conn((i + badnode) % 1000).getrawtransaction(txhash, 1)
                            break
                        except socket.error:
                            print("Problem getting raw tx from %s, retrying." % str((i + badnode) % 1000))
                            badnode += 1
                    # Get input and output objects
                    vins = tx["vin"]
                    vouts = tx["vout"]
                    # List of input reference hashes to be looked up for values
                    vinhash = []
                    # Acquire input values list
                    for vin in vins:
                        # Append vin ID and index as list to vinhash
                        try:
                            vinhash.append([vin["txid"], vin["vout"]])
                            for k in range(0, len(vinhash)+1):
                                # Get input value
                                while True:
                                    try:
                                        invals.append(conn((i + badnode) % 1000).getrawtransaction(
                                            vinhash[k][0], 1)["vout"][vinhash[k][1]]["value"])
                                        break
                                    except socket.error:
                                        print("Problem getting input value of transaction from %s, retrying." % str((i + badnode) % 1000))
                                        badnode += 1
                        except KeyError:
                            # If reference input is coinbase, it will most likely be the reason for a KeyError.
                            print("Transaction 0x%s is likely a coinbase reference. Skipping..." % txhash)
                            skipflag = False
                            break
                    # Acquire output values list
                    if skipflag:
                        for vout in vouts:
                            # Get output value
                            outvals.append(vout["value"])
                        # Calculate difference between inputs and outputs, yields fee
                        feelist.append(sum(vins)-sum(vouts))
    if skipflag:
        # return median fee in satoshis
        return int(median(feelist) * 100000000)


# Median mempool size (# of unconfirmed transactions)
def memPool():
    size = []
    for i in range(1, 1001):
        try:
            size.append(conn(i).getmempoolinfo()['size'])
        except:
            print("Problem getting mempool size from %s, skipping." % str(i))
    return int(median(size))