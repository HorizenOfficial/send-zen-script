# -*- coding: utf-8 -*-

# from __future__ import print_function
import subprocess
import sys
import os
import urllib
import json
import requests
import common

__author__ = "Lukas Bures"
__copyright__ = "Copyright 2017"
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Lukas Bures"
__email__ = "lukas@zensystem.io"
__status__ = "Production"

# Set this params
YOUR_PRIVATE_KEY = "PUT_YOUR_PRIVATE_KEY_HERE"
ZENCLI_PATH = "./zen-cli -testnet"

json_data = common.load("transaction_to_sign")

raw_tx = json_data["raw_tx"]
utxo_to_sign = json_data["utxo_to_sign"]

# SIGN RAW TRANSACTION
# delete all files in next folder
# filelist = [f for f in os.listdir("./next/") if f.endswith(".json")]
# for f in filelist:
#     os.remove(f)

# ./zen-cli
# signrawtransaction $RAW_TX
# '''
# [
#    {
#       "txid": "'$UTXO_TXID'",
#       "vout": '$UTXO_VOUT',
#       "scriptPubKey": "'$UTXO_OUTPUT_SCRIPT'",
#       "redeemScript": "'$redeemScript'"
#    }
# ]
# ''' '''
# [
#    “PRIVATE_KEY1"
# ]'''

ARG1 = "\'" + raw_tx + "\'"
ARG3 = "\'[\"" + str(YOUR_PRIVATE_KEY) + "\"]\'"

command = ZENCLI_PATH + " signrawtransaction " + ARG1 + " " + utxo_to_sign + " " + ARG3

# print command
proc = subprocess.Popen([command], stdout=subprocess.PIPE, shell=True)
(out, err) = proc.communicate()

if len(out) == 0:
    raise Exception("Bad signrawtransaction command")

out_parsed = json.loads(out)

if out_parsed.get("complete") is True:
    print "Signing complete! Transaction can be sent to the network!"
    print "Raw transaction: " + out_parsed["hex"]
    common.save(out_parsed["hex"], "transaction_complete")
    exit()

# transaction is not ready yet so prepare data for the next signer
# save to the file raw tx and prepared set of outputs to sign
json_data = {"raw_tx" : out_parsed["hex"],
             "utxo_to_sign" : utxo_to_sign}

common.save(json_data, "transaction_to_sign")

print "ALL OK!"

