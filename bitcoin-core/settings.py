#/usr/bin/python3
# Start and end times for import.
from time import time
# Set local experiment start time as Epoch
genesis = int(time())
# Set end time as Epoch
timeout = genesis+432000
size = int(input("Network size? "))+1
starttps = int(input("Starting TPS rate? "))+1