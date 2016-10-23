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

    args = parser.parse_args()

    request(args)

    