#!/usr/bin/env python

import argparse
import requests
import sys

def request(args):

    url = args.url + "/get-pet/" + args.name

    response = requests.get(url)

    if response.status_code == 404:
        if args.expect_404:
            sys.exit(0)
        else:
            sys.stderr.write(response.text + "\n")
    elif response.status_code != 200:
        raise ValueError("Unrecognied response")
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

    parser.add_argument('--expect_404',
        help="Do not print to std_err if a 4004occurs",
        default=False, dest="expect_404", action="store_true")

    args = parser.parse_args()

    request(args)

    