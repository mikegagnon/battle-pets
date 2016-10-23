#!/usr/bin/env python

import argparse
import json
import requests
import sys

def request(args):

    data = {
        "name": args.name,
        "strength": args.strength,
        "agility": args.agility,
        "wit": args.wit,
        "senses": args.senses,
    }

    response = requests.post(args.url + "/new-pet", data=json.dumps(data),
        headers = {'content-type': 'application/json'})

    if response.status_code == 400:
        if args.expect_400:
            sys.exit(0)
        else:
            sys.stderr.write(response.text)
            sys.stderr.flush()
            sys.exit(1)

    elif response.status_code != 200:
        raise ValueError("Unrecognied response")

    sys.stdout.write(response.text,)
    sys.stdout.flush()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(prog='new_pet.py')

    parser.add_argument('--url', nargs='?',
        help="The URL of the Management service",
        default="http://localhost:5000", dest="url", type=str)

    parser.add_argument('--name', nargs='?',
        help="Name of the pet",
        default="foo", dest="name", type=str)

    parser.add_argument('--strength', nargs='?',
        help="Strength of the pet",
        default=0.25, dest="strength", type=float)

    parser.add_argument('--agility', nargs='?',
        help="Agility of the pet",
        default=0.25, dest="agility", type=float)

    parser.add_argument('--wit', nargs='?',
        help="Wit of the pet",
        default=0.25, dest="wit", type=float)

    parser.add_argument('--senses', nargs='?',
        help="Senses of the pet",
        default=0.25, dest="senses", type=float)

    parser.add_argument('--expect_400',
        help="Do not print to std_err if a 400 occurs",
        default=False, dest="expect_400", action="store_true")

    args = parser.parse_args()

    request(args)

    