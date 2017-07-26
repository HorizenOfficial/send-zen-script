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
    ZENCLI_PATH = "./zen-cli -testnet"
else:
    ZENCLI_PATH = "./zen-cli"

paths = glob.glob("./utxo/transaction_to_sign_*.json")

for idx, path in enumerate(paths):
    print "Processing:" + path
    json_data = load(path)

    raw_tx = json_data["raw_tx"]
    utxo_to_sign = json_data["utxo_to_sign"]

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
        print "Saving raw transaction to the file:" + "./next/transaction_complete_" + str(idx) + ".json"
        save(out_parsed["hex"], "./next/transaction_complete_" + str(idx) + ".json")

        # --------------------------------------------------------------------------------------------------------------
        # sendrawtransaction
        print "Spending raw transaction ...",
        ARG1 = "\"" + str(out_parsed["hex"]) + "\""

        command = ZENCLI_PATH + " sendrawtransaction " + ARG1
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
