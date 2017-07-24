# Checklist
- Check version of your `zend` and `zen-cli`
    - `./zend -version`
    - `./zen-cli -version`
    
# How to run
- run `zend`
- let it sync
    - if you are _1st_ signature:
        - fill `SEND_TO_ADDRESS = "PUT_DESTINATION_ADDRESS_HERE"` in `1st.py`
        - fill `YOUR_PRIVATE_KEY = "PUT_YOUR_PRIVATE_KEY_HERE"` in `1st.py`
        - fill `YOUR_REDEEM_SCRIPT = "PUT_YOUR_REDEEM_SCRIPT_HERE"` in `1st.py`
        - run `1st.py`
        - outputs are written to **_utxo_** folder
        - pack your **_utxo_** folder and send it to next signature
    - else you are _2nd_ or next signature:
        - get the **_utxo_** folder from _1st_ signature or **_next_** folder from previous signature
        - put all files to **_utxo_** folder
        - fill `YOUR_PRIVATE_KEY = "PUT_YOUR_PRIVATE_KEY_HERE"` in `next.py`
        - fill `YOUR_REDEEM_SCRIPT = "PUT_YOUR_REDEEM_SCRIPT_HERE"` in `next.py`
        - run `next.py`
        - outputs are written to **_next_** folder
        - transactions are confirmed or send **_next_** folder to the next signature
