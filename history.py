#!/usr/bin/env python

import argparse
import json
import requests
import sys
import time

POLL_SLEEP_TIME = 0.1

def request(args):

    url = args.url + "/history"

    response = requests.get(url)

    output = json.dumps(response.json(), indent=4) + "\n"
    sys.stdout.write(output)
    sys.stdout.flush()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(prog='history.py')

    parser.add_argument('--url', nargs='?',
        help="The URL of the Arena service",
        default="http://localhost:5001", dest="url", type=str)

    args = parser.parse_args()

    request(args)

    