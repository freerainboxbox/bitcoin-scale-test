# bitcoin-scale-test
Bootstrap and automation script for a 1000 node regtest scalability experiment.\
Intended for use on Google Cloud Compute, using a command instance to hold the files.
Depends:\
Python 3.X.X\
[jgarzik/python-bitcoinrpc](https://github.com/jgarzik/python-bitcoinrpc)
bitcoind (at dust limit 0.00000001 satoshi/kB)

Set RPC credentials as "test" and "test".

Uses the subnet 142.0.0.0/20. Modify the `getIP()` function for your own use.

Will add more blockchains moving forward, including Ethereum.

Also includes sequential vanity addresses with private keys for nodes 0000 to 2000 (only 1000 were used).
