# bitcoin-scale-test
Bootstrap and automation script for a 1000 node regtest scalability experiment.\
Intended for use on Google Cloud Compute, using a command instance to hold the files.
Depends:\
Python 3.X.X\
[jgarzik/python-bitcoinrpc](https://github.com/jgarzik/python-bitcoinrpc)

Uses the subnet 142.0.0.0/20. Modify the `getIP()` function for your own use.
