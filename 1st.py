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

# 1. scans blockchain and for each transaction associated with CF utxo and adds the txid to list
# 2. for each UTXO_TXID in list, get output script (hex) and vout (`getrawtransaction`)
# 3. for each UTXO_TXID in list, `createrawtransaction` and `signrawtransaction`
# 4. Add hex outputs to another list to use as inputs for next signatory
# 5. Each signatory needs to run a version of this script with their own parameters (PRIV_KEY and redeemScript)

# ----------------------------------------------------------------------------------------------------------------------
# Set this parameters
SEND_TO_ADDRESS = "PUT_DESTINATION_ADDRESS_HERE"
YOUR_PRIVATE_KEY = "PUT_YOUR_PRIVATE_KEY_HERE"
YOUR_REDEEM_SCRIPT = "PUT_YOUR_REDEEM_SCRIPT_HERE"

UTXO_ADDRESS = "zsyF68hcYYNLPj5i4PfQJ1kUY6nsFnZkc82"
TX_FEE = 0.0001

# ----------------------------------------------------------------------------------------------------------------------
# 1a) Get all CF utxo
url = "https://explorer.zensystem.io/insight-api-zen/addrs/utxo"
response = requests.post(url, data={'addrs': UTXO_ADDRESS})
data = response.json()

if response.status_code != 200:
    raise Exception("Bad response status code: " + str(response.status_code))

# ----------------------------------------------------------------------------------------------------------------------
# 1b) Get all txid to list
UTXO_TXIDs = []
UTXO_VOUTs = []
UTXO_AMOUNT = []
for d in data:
    # only txids with confirmations > 100 are considered
    if d["confirmations"] > 100:
        UTXO_TXIDs.append(d["txid"])
        UTXO_VOUTs.append(d["vout"])
        UTXO_AMOUNT.append(d["amount"])

# ----------------------------------------------------------------------------------------------------------------------
# 2) for each UTXO_TXID in list, get output script (hex)
# and vout (`getrawtransaction`) - this has been found already
UTXO_OUTPUT_SCRIPTs = []  # hex
LENGHT = str(len(UTXO_TXIDs))
for idx, UTXO_TXID in enumerate(UTXO_TXIDs):
    print "getrawtransaction: " + str(idx + 1) + " / " + LENGHT

    proc = subprocess.Popen(["./zen-cli getrawtransaction \"" + str(UTXO_TXID) + "\" 1"], stdout=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()
    # print "program output:", out
    json_parsed = json.loads(out)
    UTXO_OUTPUT_SCRIPTs.append(json_parsed["hex"])

# ----------------------------------------------------------------------------------------------------------------------
# 3a) for each UTXO_TXID in list, `createrawtransaction`
RAW_TRANSACTIONs = []
for idx, UTXO_TXID in enumerate(UTXO_TXIDs):
    print "createrawtransaction: " + str(idx + 1) + " / " + LENGHT

    # ./zen-cli
    # createrawtransaction
    # '''
    # [
    #    {
    #       "txid": "'$UTXO_TXID'",
    #       "vout": '$UTXO_VOUT'
    #    }
    # ]
    # ''' '''
    # {
    #    "'$NEW_ADDRESS'": 1.4999
    # }'''
    command = "./zen-cli createrawtransaction \'[{\"txid\": \"" + str(UTXO_TXID) + "\", \"vout\": " \
              + str(UTXO_VOUTs[idx]) + "}]\' \'{\"" + SEND_TO_ADDRESS + "\": " + str(UTXO_AMOUNT[idx] - TX_FEE) + "}\'"
    # print command
    proc = subprocess.Popen([command], stdout=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()
    RAW_TRANSACTIONs.append(out)

# ----------------------------------------------------------------------------------------------------------------------
# 3b) for each UTXO_TXID in list `signrawtransaction`
# delete all files in utxo folder
filelist = [f for f in os.listdir("./utxo/") if f.endswith(".json")]
for f in filelist:
    os.remove(f)

for idx, raw in enumerate(RAW_TRANSACTIONs):
    print "signrawtransaction: " + str(idx + 1) + " / " + LENGHT
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
    command = "./zen-cli signrawtransaction " + str(raw) + "\'[{\"txid\": \"" + str(UTXO_TXID) + "\"," \
                                                              " \"vout\": " + str(UTXO_VOUTs[idx]) + "," \
                                                              " \"scriptPubKey\": \"" + str(UTXO_OUTPUT_SCRIPTs[idx]) + "\","\
                                                              " \"redeemScript\": \"" + str(YOUR_REDEEM_SCRIPT) + \
                                                              "\"}]\' \'[\"" + str(YOUR_PRIVATE_KEY) + "\"]\'"
    # print command
    proc = subprocess.Popen([command], stdout=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()
    json_parsed = json.loads(out)
    # RAW_TRANSACTIONs.append(out)
    # print json_parsed
    common.save(json_parsed, str(UTXO_TXIDs[idx]))

print "ALL OK!"
