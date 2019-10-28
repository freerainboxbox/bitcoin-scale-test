import json
import csv
import random as rng
from progress.bar import IncrementalBar as Bar
size = int(input("Network size? "))
starttps = int(input("Start TPS? "))
endtps = int(input("End TPS? "))
outfile = input("Name of output file? ")


def getAddr(node):
    # Retrieve address from vanity CSV store
    with open("addresses.csv") as addresses:
        addrlist = list(csv.reader(addresses))
        return addrlist[node][1]


def paramGen(tps, parameters, bar):
    node = []
    txns = []
    prevdelay = 0
    for i in range(1, tps*3600+1):
        node.append(rng.sample(range(1, size+1), 2))
        txns.append((node[i-1][0], "sendtoaddress", (getAddr(node[i-1][1]), 0.00000001),
                     float((i/tps)+prevdelay), "From %s to %s\n" % (node[i-1][0], node[i-1][1])))
        bar.next()
    parameters.update({tps: txns})
    if (tps < endtps):
        tps += 1
        prevdelay += 3600
        print("\n%s" % tps)
        print(parameters)
        return paramGen(tps, parameters, bar)
    else:
        bar.finish()
        print(json.dumps(parameters))
        return json.dumps(parameters)


def totalCount(start, end):
    x = 0
    for i in range(start, end+1):
        x += i*3600
    return x


def main():
    parameters = {}
    if (starttps <= endtps):
        bar = Bar('Generating', max=totalCount(starttps, endtps))
        endparameters = paramGen(starttps, parameters, bar)
        f = open(outfile, "w+")
        f.write(endparameters)
        f.close()
    else:
        raise Exception("Start TPS must be less than or equal to end TPS.")

if __name__ == '__main__':
    main()
