#/usr/bin/python3
# Start and end times for import.
from time import time
import json
# Set local experiment start time as Epoch
genesis = int(time())
# Set end time as Epoch
size = int(input("Network size? "))
starttps = int(input("Starting TPS rate? "))
endtps = int(input("Ending TPS rate? "))
paramfn = input("Name of parameters file: ")
paramjson = open(paramfn,"r")
parameters = json.load(paramjson)
paramjson.close()
genesis = int(time())
timeout = genesis+3600*(1+endtps-starttps)