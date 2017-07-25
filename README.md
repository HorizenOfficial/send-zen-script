# Checklist
- Check version of your `zend` and `zen-cli`
    - `./zend -version`
    - `./zen-cli -version`
    
# How to run
- put your `zend` and `zen-cli` binaries to the `send-zen-script` folder
- run `zend`
- let it sync
    - if you are _**1st**_ signature:
        - check `TEST_NETWORK = False` parameter, it has to be `False`, then script run on ZEN mainnet 
        - fill `SEND_TO_ADDRESS = "PUT_DESTINATION_ADDRESS_HERE"` in `1st.py`
        - fill `YOUR_PRIVATE_KEY = "PUT_YOUR_PRIVATE_KEY_HERE"` in `1st.py`
        - fill `YOUR_REDEEM_SCRIPT = "PUT_YOUR_REDEEM_SCRIPT_HERE"` in `1st.py`
        - fill `SEND_UTXO_AMOUNT = 10` in `1st.py` (10 is only example) - that is number of UTXOs which will be spend, e.g.: 10 = (10UTXOs * 1,5CF ZENs) - TX_FEE = ammount of ZENs 
        - run `1st.py`
        - outputs are written to **_next_** folder
        - pick `transaction_to_sign.json` file from your **_next_** folder and send it to next signature
    - else you are _**2nd**_ or next signature:
        - get the `transaction_to_sign.json` file from the previous signature and put it to **_utxo_** folder
        - check `TEST_NETWORK = False` parameter, it has to be `False`, then script run on ZEN mainnet
        - fill `YOUR_PRIVATE_KEY = "PUT_YOUR_PRIVATE_KEY_HERE"` in `next.py`
        - run `next.py`
            - if outputs are written to **_next_** folder
                - send `transaction_to_sign.json` file to the next signature
            - else transactions are confirmed
                - raw transaction (hex) is saved to **_next_** folder to `transaction_complete.json` file
