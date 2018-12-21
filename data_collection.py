#!/usr/bin/python3
# Preamble
from subprocess import check_output
from nodetools import conn
from statistics import median
from math import floor
from time import time
from random import randint

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
    # Get fee for all nodes (maximum wait time is 1008 blocks)
    for i in range(1, 1001):
        rawfee.append(conn(i).estimatesmartfee(1008))
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
        except KeyError:
            # Occasionally, there will be a KeyError. If so, return None.
            pass


'''
AtomMedFee estimator
Bitcoin JSON-RPC API provides no straightforward way to get transaction fees.
By getting transactions' total input and output, the fees can be calculated by finding the difference.
'''
def medFee(tps):
    # TPS interval start block height
    startht = tps * 6 + 200000
    # Get data from 3 nodes
    match = True
    while match:
        data1 = randint(1,1000)
        data2 = randint(1,1000)
        data3 = randint(1,1000)
        if data1 != data2 != data3:
            match = False
            for i in [data1, data2, data3]:
                feelist = []
                # Serialized block with txhashes
                rawblock = []
                # List of txhashes
                txlist = []
                # List of inputs/outputs
                vins = []
                vouts = []
                for j in range(startht, startht + 7):
                    # Get serialized block
                    rawblock = conn(i).getblock(conn(i).getblockhash(j))
                    # Get transaction hash list
                    txlist = rawblock["tx"]
                    for txhash in txlist:
                        # Coinbase error flag
                        skipflag = True
                        # Input/output values
                        invals = []
                        outvals = []
                        # Get raw transaction
                        tx = conn(i).getrawtransaction(txhash, 1)
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
                                    invals.append(conn(i).getrawtransaction(
                                        vinhash[k][0], 1)["vout"][vinhash[k][1]]["value"])
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
        size.append(conn(i).getmempoolinfo()['size'])
    return int(median(size))