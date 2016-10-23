#!/usr/bin/env python

import argparse
import json
import requests
import sys
import time

POLL_SLEEP_TIME = 0.1

def request(args):

    url = args.url + "/arena-result/" + args.jobid

    response = requests.get(url)

    if response.status_code == 404 or response.status_code == 500:
        sys.stderr.write(response.text)
        sys.stderr.flush()
        sys.exit(1)

    if response.status_code == 102:
        print "The contest is still processing"
        sys.exit(0)

    sys.stdout.write(response.text + "\n")
    sys.stdout.flush()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(prog='new_pet.py')

    parser.add_argument('--url', nargs='?',
        help="The URL of the Arena service",
        default="http://localhost:5001", dest="url", type=str)

    parser.add_argument('--jobid', nargs='?',
        help="Name of the pet to battle", dest="jobid", type=str, required=True)

    args = parser.parse_args()

    request(args)

    