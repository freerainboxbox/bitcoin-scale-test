#!/usr/bin/python3
# Preamble
from subprocess import check_output
from statistics import median
from math import floor
from time import time
from bitcoinrpc.authproxy import AuthServiceProxy,JSONRPCException
import random as rng
import socket
from nodetools import conn, localConn, getIP
from settings import size, genesis

'''
These functions collect the dependent variables (DVs).
They are:
Atomic Minimum Fee (AtomMinFee)
Atomic Median Fee (AtomMedFee)
Unconfirmed Transaction Pool Size (MemPool)
'''

# AtomMinFee estimator
# Likely will not return any data until the mempool size can stay large enough for the fee estimator to work.


def minFee():
    rawfee = []
    fee = []
    datapt = open("MinFee.csv", "a+")
    # Get fee for all nodes (maximum wait time is 1008 blocks)
    for i in range(1, size+1):
        try:
            rawfee.append(localConn(i, "estimatesmartfee", (1008,), 0, ""))
        except socket.error:
            print("Trouble getting minfee from node %s, skipping." % str(i))
            datapt.close()
    for i in range(0, size):
        try:
            # When the mempool isn't large enough
            if rawfee[i]["errors"] == ['Insufficient data or no feerate found']:
                datapt.close()
            else:
                # get fee list
                for j in range(0, size):
                    fee.append(rawfee[j]['feerate'] * 100000000)
                # write to fee list
                datapt.write("%s,%s\n" % (str(int(time())-genesis),str(int(median(fee)))))
                datapt.close()
        except:
            # Occasionally, there will be a KeyError. If so, close the I/O object and exit.
            datapt.close()


'''
AtomMedFee estimator
Bitcoin JSON-RPC API provides no straightforward way to get transaction fees.
By getting transactions' total input and output, the fees can be calculated by finding the difference.
'''
def medFee(tps):
    # TPS interval start block height
    startht = tps * 6 + 1323
    datapt = open("MedFee.csv","a+")
    # Get data from 3 nodes
    while True:
        nodes = rng.sample(range(1, size+1), 3)
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
                        # Modulo network size to prevent node selection out of range.
                        rawblock = localConn(
                            (i+badnode) % size, "getblock", (localConn((i+badnode) % size, "getblockhash", (j), 0, "")), 0, "")
                        break
                    except socket.error:
                        print("Problem getting block from %s, retrying." %
                              str((i + badnode) % size))
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
                            tx = localConn((i+badnode) % size,
                                      "getrawtransaction", (txhash, 1), 0, "")
                            break
                        except socket.error:
                            print("Problem getting raw tx from %s, retrying." %
                                  str((i + badnode) % size))
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
                                        invals.append(localConn(
                                            (i + badnode) % size, "getrawtransaction", (vinhash[k][0]), 0, "")["vout"][vinhash[k][1]]["value"])
                                        break
                                    except socket.error:
                                        print("Problem getting input value of transaction from %s, retrying." % str(
                                            (i + badnode) % size))
                                        badnode += 1
                        except KeyError:
                            # If reference input is coinbase, it will most likely be the reason for a KeyError.
                            print(
                                "Transaction 0x%s is likely a coinbase reference. Skipping..." % txhash)
                            skipflag = False
                            break
                    # Acquire output values list
                    if skipflag:
                        for vout in vouts:
                            # Get output value
                            outvals.append(vout["value"])
                        # Calculate difference between inputs and outputs, yields fee
                        feelist.append(sum(invals)-sum(outvals))
    if skipflag:
        # return median fee in satoshis
        datapt.write("%s,%s\n" % (str(floor((int(time())-genesis)/3600)),str(int(median(feelist) * 100000000))))
        datapt.close()


# Median mempool size (# of unconfirmed transactions)
def memPool():
    memSize = []
    datapt = open("MemPool.csv","a+")
    for i in range(1, size+1):
        try:
            memSize.append(int(localConn(i, "getmempoolinfo", tuple(), 0, ""))["size"])
        except:
            print("Problem getting mempool size from %s, skipping." % str(i))
    datapt.write("%s,%s\n" % (str(int(time())-genesis),str(int(median(memSize)))))
    datapt.close()