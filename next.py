# -*- coding: utf-8 -*-
import subprocess
import json
import glob

__author__ = "Lukas Bures"
__copyright__ = "Copyright 2017"
__license__ = "MIT"
__version__ = "0.0.2"
__maintainer__ = "Lukas Bures"
__email__ = "lukas@zensystem.io"
__status__ = "Production"

# ----------------------------------------------------------------------------------------------------------------------
# Set this params
TEST_NETWORK = False  # True = it uses -testnet, False = mainnet
YOUR_PRIVATE_KEY = "PUT_YOUR_PRIVATE_KEY_HERE"
ZEN_RPC_IP = "127.0.0.1"
ZEN_RPC_USER="PUT_YOUR_ZEND_RPC_USER_HERE"
ZEN_RPC_PASSWORD="PUT_YOUR_ZEND_RPC_PASSWORD_HERE"

# ----------------------------------------------------------------------------------------------------------------------
# IO functions
def save(data, path):
    with open(path, 'w') as outfile:
        json.dump(data, outfile)


def load(path):
    with open(path) as json_data:
        data = json.load(json_data)
    return data

# ----------------------------------------------------------------------------------------------------------------------
# loading and setting parameters
if TEST_NETWORK:
    ZEN_RPC_PORT="18231"
else:
    ZEN_RPC_PORT="8231"

paths = glob.glob("./utxo/transaction_to_sign_*.json")
postpath = "./postdata.json"

for idx, path in enumerate(paths):
    print "Processing:" + path
    json_data = load(path)

    raw_tx = json_data["raw_tx"]
    utxo_to_sign = json_data["utxo_to_sign"]
    utxo_to_sign_no_singlequote = utxo_to_sign.replace("'", "")

    # ------------------------------------------------------------------------------------------------------------------
    # SIGN RAW TRANSACTION
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

    POSTDATA = {"jsonrpc": "1.0", "id":"curltest", "method": "signrawtransaction", "params": [ raw_tx, json.loads(utxo_to_sign_no_singlequote) ,[YOUR_PRIVATE_KEY]]}
    save(POSTDATA, postpath)

    command = "curl -H 'content-type: text/plain;' -d \"@" + postpath + "\" http://" + ZEN_RPC_USER + ":" + ZEN_RPC_PASSWORD + "@" + ZEN_RPC_IP + ":" + str(ZEN_RPC_PORT)

    proc = subprocess.Popen([command], stdout=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()

    # overwrite postdata.json, contains privkey
    save({}, postpath)

    if len(out) == 0:
        raise Exception("Bad signrawtransaction command")

    out_parsed = json.loads(out)["result"]

    if out_parsed.get("complete") is True:
        print "Signing complete! Transaction can be sent to the network!"
        print "Raw transaction: " + out_parsed["hex"]
        print "Saving raw transaction to the file:" + "./next/transaction_complete_" + str(idx) + ".json"
        save(out_parsed["hex"], "./next/transaction_complete_" + str(idx) + ".json")

        # --------------------------------------------------------------------------------------------------------------
        # sendrawtransaction
        print "Spending raw transaction ...",
        POSTDATA = {"jsonrpc": "1.0", "id":"curltest", "method": "sendrawtransaction", "params": [out_parsed["hex"]]}
        save(POSTDATA, postpath)

        proc = subprocess.Popen([command], stdout=subprocess.PIPE, shell=True)
        print "done"
        print ""
    else:
        # transaction is not ready yet so prepare data for the next signer
        # save to the file raw tx and prepared set of outputs to sign
        json_data = {"raw_tx": out_parsed["hex"], "utxo_to_sign": utxo_to_sign}
        save(json_data, path.replace("utxo", "next"))

print "You have to send /next/transaction_to_sign_X.json files (where X is number of chunk) to next signature."
print "ALL OK!"
