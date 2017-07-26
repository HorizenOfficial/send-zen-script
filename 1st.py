# -*- coding: utf-8 -*-
import subprocess
import json
import requests

__author__ = "Lukas Bures"
__copyright__ = "Copyright 2017"
__license__ = "MIT"
__version__ = "0.0.2"
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
TEST_NETWORK = False  # True = it uses -testnet, False = mainnet
SEND_TO_ADDRESS = "PUT_DESTINATION_ADDRESS_HERE"
YOUR_PRIVATE_KEY = "PUT_YOUR_PRIVATE_KEY_HERE"

# how many UTXOx should be spent. Note that there is a maximum limit of 100KB per tx,
# so effectively around 1900 UTXOs can be spent in one transaction
# (this is a raw calculation, probably it could be more).
SEND_UTXO_AMOUNT = 10  # e.g.: 10 UTXOs is equal to (10*1,5)-TX_FEE ZENs
TX_FEE = 0.0001

if TEST_NETWORK:
    UTXO_ADDRESS = "zrRBQ5heytPMN5nY3ssPf3cG4jocXeD8fm1"
    ZENCLI_PATH = "./zen-cli -testnet"
    # Redeem script is constant to the set of signers. So don't change it unless there is a new set of signers
    YOUR_REDEEM_SCRIPT = "522103463492c6b015726cbc6bca1535acc2d4d23a2d6836f430765c5d936d49e353b0210238cab01744382b3ab77cd332f7560aee7a114ee7a07a9fe1c203ce7a2beed53c2102fa845c37c198d2d60418d9cab9ac64700662ba7a0b99b9570d4ba2c36d268e8753ae"
    URL = "http://aayanl.tech:8081/insight-api-zen/addrs/utxo"
else:
    UTXO_ADDRESS = "zsyF68hcYYNLPj5i4PfQJ1kUY6nsFnZkc82"
    ZENCLI_PATH = "./zen-cli"
    # Redeem script is constant to the set of signers. So don't change it unless there is a new set of signers
    YOUR_REDEEM_SCRIPT = "PUT_REDEEM_SCRIPT_HERE"
    URL = "https://explorer.zensystem.io/insight-api-zen/addrs/utxo"


# ----------------------------------------------------------------------------------------------------------------------
# IO functions
def save(data, name):
    with open("./next/" + name + '.json', 'w') as outfile:
        json.dump(data, outfile)


def load(path):
    with open("./utxo/" + path + '.json') as json_data:
        data = json.load(json_data)
    return data

# ----------------------------------------------------------------------------------------------------------------------
# 1a) Get all CF utxo
response = requests.post(URL, data={'addrs': UTXO_ADDRESS})
data = response.json()

if response.status_code != 200:
    raise Exception("Bad response status code: " + str(response.status_code))

# ----------------------------------------------------------------------------------------------------------------------
# 1 Get all txid to list
UTXO_TXIDs = []
UTXO_VOUTs = []
UTXO_OUTPUT_SCRIPTs = []
UTXO_TOTAL_AMOUNT = 0
for d in data:
    # only txids with confirmations > 100 are considered
    if d["confirmations"] > 100:
        UTXO_TXIDs.append(d["txid"])
        UTXO_VOUTs.append(d["vout"])
        UTXO_OUTPUT_SCRIPTs.append(d["scriptPubKey"])
        UTXO_TOTAL_AMOUNT += d["amount"]

        if len(UTXO_TXIDs) >= SEND_UTXO_AMOUNT:
            break

if len(UTXO_TXIDs) != SEND_UTXO_AMOUNT:
    raise Exception("Not enough funds. Only " + str(len(UTXO_TXIDs)) + "spendable UTXOs were found.")


# ----------------------------------------------------------------------------------------------------------------------
# split list to the chunks
def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


UTXO_TXIDs_CHUNKs = list(chunks(UTXO_TXIDs, 100))

for idx, UTXO_TXIDs_CHUNK in enumerate(UTXO_TXIDs_CHUNKs):
    print "Processing chunk: " + str(idx + 1) + "/" + str(len(UTXO_TXIDs_CHUNKs))

    # ------------------------------------------------------------------------------------------------------------------
    # 2 CREATE RAW TRANSACTION
    # ./zen-cli
    # createrawtransaction
    # '''
    # [
    #    {
    #       "txid": "'$UTXO_TXID'",
    #       "vout": '$UTXO_VOUT'
    #    },
    #    {
    #       ...
    #    }
    # ]
    # ''' '''
    # {
    #    "'$NEW_ADDRESS'": 1.4999
    # }'''

    ARG1 = "\'["
    for i in range(0, len(UTXO_TXIDs_CHUNK)):
        ARG1 += "{\"txid\": \"" + str(UTXO_TXIDs_CHUNK[i]) + "\", \"vout\": " + str(UTXO_VOUTs[i]) + "},"
    ARG1 = ARG1[:-1]  # remove comma at the end
    ARG1 += "]\'"

    ARG2 = "\'{\"" + SEND_TO_ADDRESS + "\": " + str(UTXO_TOTAL_AMOUNT - TX_FEE) + "}\'"

    command = ZENCLI_PATH + " createrawtransaction " + ARG1 + " " + ARG2

    # print command
    proc = subprocess.Popen([command], stdout=subprocess.PIPE, shell=True)
    (raw_tx, err) = proc.communicate()

    if len(raw_tx) == 0:
        raise Exception("Bad createrawtransaction command")

    # ------------------------------------------------------------------------------------------------------------------
    # 3 SIGN RAW TRANSACTION
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

    ARG1 = "\'" + raw_tx.strip() + "\'"

    ARG2 = "\'["
    for i in range(0, len(UTXO_TXIDs_CHUNK)):
        ARG2 += "{\"txid\": \"" + str(UTXO_TXIDs_CHUNK[i]) + "\", " \
                "\"vout\": " + str(UTXO_VOUTs[i]) + "," \
                "\"scriptPubKey\": \"" + str(UTXO_OUTPUT_SCRIPTs[i]) + "\"," \
                "\"redeemScript\": \"" + str(YOUR_REDEEM_SCRIPT) + "\"},"
    ARG2 = ARG2[:-1]  # remove comma at the end
    ARG2 += "]\'"

    ARG3 = "\'[\"" + str(YOUR_PRIVATE_KEY) + "\"]\'"

    command = ZENCLI_PATH + " signrawtransaction " + ARG1 + " " + ARG2 + " " + ARG3

    # print command
    proc = subprocess.Popen([command], stdout=subprocess.PIPE, shell=True)
    (out, _) = proc.communicate()

    if len(out) == 0:
        raise Exception("Bad signrawtransaction command")

    out_parsed = json.loads(out)

    # save to the file raw tx and prepared set of outputs to sign
    json_data = {"raw_tx": out_parsed["hex"], "utxo_to_sign": ARG2}

    save(json_data, "transaction_to_sign_" + str(idx))

print "You have to send /next/transaction_to_sign_X.json files (where X is number of chunk) to next signature."
print "ALL OK!"
