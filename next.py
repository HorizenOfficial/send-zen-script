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


YOUR_PRIVATE_KEY = ""
YOUR_REDEEM_SCRIPT = ""

# TODO: load files in "utxo" directory
# TODO: for every file do next signature with new private key
# TODO: save output to "next" directory and send it to next signature
