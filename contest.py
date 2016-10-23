#!/usr/bin/env python

import argparse
import json
import requests
import sys
import time

POLL_SLEEP_TIME = 0.1

def request(args):

    data = {
        "name1": args.name1,
        "name2": args.name2,
        "category": args.category,
    }

    response = requests.post(args.url + "/arena", data=json.dumps(data),
        headers = {'content-type': 'application/json'})

    if response.status_code != 200:
        sys.stderr.write(str(response.status_code) + "\n")
        sys.stderr.write(response.text)
        sys.exit(1)

    if args.block:

        jobid = response.json()

        url = args.url + "/arena-result/" + jobid
        response = requests.get(url)

        while response.status_code == 102:
            print "Waiting for contest to finish"

            time.sleep(POLL_SLEEP_TIME)
            response = requests.get(url)
    
    sys.stdout.write(response.text + "\n")
    sys.stdout.flush()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(prog='new_pet.py')

    parser.add_argument('--url', nargs='?',
        help="The URL of the Arena service",
        default="http://localhost:5001", dest="url", type=str)

    parser.add_argument('--name1', nargs='?',
        help="Name of the pet to battle",
        default="foo", dest="name1", type=str)

    parser.add_argument('--name2', nargs='?',
        help="Name of the pet to battle",
        default="bar", dest="name2", type=str)

    parser.add_argument('--category', nargs='?',
        help="Category of battle. Must be one of: strength, agility, wit, " + \
             "senses",
        default="strength", dest="category", type=str)

    parser.add_argument('--unblock',
        help="Do not wait for the battle to finish",
        default=False, dest="unblock", action="store_true")

    args = parser.parse_args()

    args.block = not args.unblock

    request(args)

    