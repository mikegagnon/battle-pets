#!/usr/bin/env python

import argparse
import json
import requests
import sys

def request(url):

    data = {
        "name": "foo",
        "agility": 0.25,
        "senses": 0.25,
        "strength": 0.25,
        "wit": 0.25
    }

    response = requests.post(url + "/new-pet", data=json.dumps(data),
        headers = {'content-type': 'application/json'})

    if response.status_code != 200:
        sys.stderr.write(str(response.status_code) + "\n")
        sys.stderr.write(response.text + "\n")


if __name__ == "__main__":

    parser = argparse.ArgumentParser(prog='new_pet.py')

    parser.add_argument('--url', nargs='?',
        help="The URL of the Management service",
        default="http://localhost:5000", dest="url", type=str)

    args = parser.parse_args()

    request(args.url)

    