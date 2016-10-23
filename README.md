# Battle Pets
by Michael Gagnon

## Installation
These are the installation commands I needed to use to setup Battle Pets on a fresh install of Ubuntu.16.04.1

```
download https://bootstrap.pypa.io/get-pip.py
python get-pip.py

pip install requests
pip install Flask
pip install jsonschema
pip install redis
pip install rq

download http://download.redis.io/redis-stable.tar.gz
tar xvzf redis-stable.tar.gz
cd redis-stable
make
make install
```
## Tests

First you need to fire up Redis and an RQ worker:

```bash
$ redis-server
$ rq worker
```

### Unit tests

```bash
$ python test.py
```

### Live system test

First, fire up the services:

```bash
$ python management.py
$ python arena.py
```

Then run the test:

```bash
$ ./test.sh
```

The output should look something like `expected_test_output.txt`, but it won't be an exact match because of timestamps.

## Command-line tools

### `new_pet.py`

Creates a new pet.

```
$ python new_pet.py -h
usage: new_pet.py [-h] [--url [URL]] [--name [NAME]] [--strength [STRENGTH]]
                  [--agility [AGILITY]] [--wit [WIT]] [--senses [SENSES]]
                  [--expect_400]

optional arguments:
  -h, --help            show this help message and exit
  --url [URL]           The URL of the Management service
  --name [NAME]         Name of the pet
  --strength [STRENGTH]
                        Strength of the pet
  --agility [AGILITY]   Agility of the pet
  --wit [WIT]           Wit of the pet
  --senses [SENSES]     Senses of the pet
  --expect_400          Do not print to std_err if a 400 occurs
```

### `get_pet.py`

Retrieves information about a pet.

```
$ ./get_pet.py -h
usage: new_pet.py [-h] [--url [URL]] [--name [NAME]] [--expect_404]

optional arguments:
  -h, --help     show this help message and exit
  --url [URL]    The URL of the Management service
  --name [NAME]  Name of the pet
  --expect_404   Do not print to std_err if a 4004occurs
```

### `contest.py`

Initiates a battle between two pets.
By default, `contest.py` blocks until the contest has completed.

```
$ ./contest.py -h
usage: new_pet.py [-h] [--url [URL]] [--name1 [NAME1]] [--name2 [NAME2]]
                  [--category [CATEGORY]] [--unblock] [--expect_400]

optional arguments:
  -h, --help            show this help message and exit
  --url [URL]           The URL of the Arena service
  --name1 [NAME1]       Name of the pet to battle
  --name2 [NAME2]       Name of the pet to battle
  --category [CATEGORY]
                        Category of battle. Must be one of: strength, agility,
                        wit, senses
  --unblock             Do not wait for the battle to finish
  --expect_400          Expect a 400 error
```

### `history.py`

```
$ ./history.py -h
usage: new_pet.py [-h] [--url [URL]]

optional arguments:
  -h, --help   show this help message and exit
  --url [URL]  The URL of the Arena service
```


## Bottom

ERRATA:

- Never built a REST service before
- Unfamiliar with HTTP error codes, so I may be generating inappropriate
  errors
- Never used Flask or sqlite before
- Unfamiliar with conventions for git commit messages
- It's been about 12 years since I've used SQL
- It's been about 12 years since I've professionally coded in Python,
  so my style is probably off. For example, unit tests
- Unfamiliar with PEP 8 style
- Never used a job queue before
- No security built in
- Using polling instead of callbacks
- db connection in battle
- testing for failed jobs
- didn't use git branch
- Redis necessary for test
- Server error messages not conventional
- TDD

TODO high priority
- README
- Internal documentation
- Test on linux

TODO low priority
- Training interface: reports the most high value matches
- Leader board
