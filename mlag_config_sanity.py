import csv
from jsonrpclib import Server
import ssl
from getpass import getpass
import argparse

ssl._create_default_https_context = ssl._create_unverified_context

parser = argparse.ArgumentParser()
parser.add_argument('--username', required=True)
parser.add_argument('--inventoryname', required=True)

args = parser.parse_args()
switchuser = args.username
inventory = args.inventoryname
switchpass = getpass()
command_string = "show mlag config-sanity"

def printLastkey(d):
    peerValue = {}
    localValue = {}
    for key, value in d.items():
        if isinstance(value, dict):
            print(key)
            printLastkey(value)
        else:
            if key == "localValue":
                localValue = value.split(",")
            if key == "peerValue":
                peerValue = value.split(",")
        if peerValue != {} and localValue != {}:
            print list(set(localValue) - set(peerValue))
            print list(set(peerValue) - set(localValue))

with open(inventory) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    for iter,row in enumerate(csv_reader):
        if iter != 0 :
            ssh_host = row[5]
            hostname = row[0]
            model = row[2]
            if model != "vEOS" and not hostname.startswith("sw-"):
                urlString = "https://{}:{}@{}/command-api".format(switchuser, switchpass, ssh_host)
                switchReq = Server(urlString)
                response = switchReq.runCmds( 1, ["enable", command_string] )
                if response[1]["globalConfiguration"] != {} or response[1]["interfaceConfiguration"] != {}:
                    print "\n"+ hostname
                    print "MLAG inconsistencies found"
                    print response[1]["globalConfiguration"]
                    printLastkey(response[1]["interfaceConfiguration"])
