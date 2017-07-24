# -*- coding: utf-8 -*-

import json

__author__ = "Lukas Bures"
__copyright__ = "Copyright 2017"
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Lukas Bures"
__email__ = "lukas@zensystem.io"
__status__ = "Production"


def save(data, name):
    with open("./utxo/" + name + '.json', 'w') as outfile:
        json.dump(data, outfile)


def load(path):
    with open(path) as json_data:
        data = json.load(json_data)
    return data
