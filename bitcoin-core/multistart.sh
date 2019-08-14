#!/bin/bash
for id in {1..10..1}
    do
        echo "init proxy $id"
        mkdir "nodedata/${id}"
        screen -dmS "${id}_proxy" bash -c "throttle-proxy -p `expr $id + 21000` -d 300; exec $SHELL"
        echo "init btc $id"
        echo "-datadir=\"${PWD}/nodedata/${id}\""
        screen -dmS "${id}_bitcoin" bash -c "bitcoind -regtest -blocknotify=\"New best chaintip %s\" -datadir=\"${PWD}/nodedata/${id}/\" -debuglogfile=debug.log -listen -proxy=`expr $id + 21000` -rpcallowip=0.0.0.0/0 -rpcbind=127.0.0.1 -port=`expr $id + 22000` -rpcport=`expr $id + 23000` -rpcuser=user -rpcpassword=pw -dustrelayfee=0 ; exec bash"
    done
