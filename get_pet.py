#!/usr/bin/env python

import argparse
import requests
import sys

def request(args):

    url = args.url + "/get-pet/" + args.name

    response = requests.get(url)

    if response.status_code != 200:
        sys.stderr.write(str(response.status_code) + "\n")
        sys.stderr.write(response.text + "\n")
    else:
        print response.text


if __name__ == "__main__":

    parser = argparse.ArgumentParser(prog='new_pet.py')

    parser.add_argument('--url', nargs='?',
        help="The URL of the Management service",
        default="http://localhost:5000", dest="url", type=str)

    parser.add_argument('--name', nargs='?',
        help="Name of the pet",
        default="foo", dest="name", type=str)

    args = parser.parse_args()

    request(args)

    