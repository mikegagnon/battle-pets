# Battle Pets
by Michael Gagnon

## Installation
These are the installation commands I used setup Battle Pets on a fresh install of Ubuntu.16.04.1

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
  --expect_404   Do not print to std_err if a 404w occurs
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
## Architecture decisions

I chose Python because I love the language 

The services are implemented in Flask. I chose Flask because it's a
microframework, and thus has a low barrier to entry. I've never coded
a REST service before, so barrier to entry was important.

In similar reasoning for my choice for Flask, I chose RQ and Redis
to handle the contest workers and the queue. RQ markets itself as
"simple job queues."

I chose to use JSON as the communcation protcol because it is easy to
work with and is well supported by Python and Flask.


## REST interfaces

### `[management service]/new-pet`

You can creete new pets by posting JSON to `[management service]/new-pet`.

Here is an example JSON request:

```JSON
 {
    "name": "Charmander",
    "strength": 0.1,
    "agility": 0.2,
    "wit": 0.5,
    "senses": 0.2
}
```

The sum of `(strength, agility, wit, senses)` must be <= 1.0.
Furthermore, each attribute must be <= 1.0 and >= 0.

The length of `name` must be <= 100.

**Possible responses**:

- Upon success, `/new-pet` responds with a "200 OK" status code, with
  an empty body. Choosing to return an empty body follows the 
  UNIX tradition of producing no output upon success.
- If the post to `/new-pet` is not JSON, then it responds with
  a "400 BAD REQUEST" status code, along with 
  `{"message": "No JSON object could be decoded"}`
- If the name is already taken, `/new-pet` resonds with
  a "400 BAD REQUEST" status code, along with 
  `{"message": "A pet with the name '[name]' already exists."}`
- If either (1) the sum of the attributes > 1.0, or (2)
  the name exceeds max length, then `/new-pet` responds with
  a "400 BAD REQUEST" status code, along with 
  `{"message": "The sum of (strength, agility, wit, senses) must be <= 1.0 AND the length of name must be <= 100."}`
  It would be preferable to give each of these cases unique error messages, rather then clumping them into one.
  However, I did not implement it that way to due to time constraints and it seems like a low priority change.
  

Here is the JSON Schema for `/new-pet` requests:

```JSON
NEW_PET_REQUEST_SCHEMA = {
    "type": "object",
    "properties": {
        "name": {
            "type": "string"
        },
        "strength": {
            "type": "number",
            "minimum": 0,
            "maximum": 1
        },
        "agility": {
            "type": "number",
            "minimum": 0,
            "maximum": 1
        },
        "wit": {
            "type": "number",
            "minimum": 0,
            "maximum": 1
        },
        "senses": {
            "type": "number",
            "minimum": 0,
            "maximum": 1
        }
    },
    "required": ["name", "strength", "agility", "wit", "senses"]
}
```

### `[management service]/get-pet/<string:petname>`

You can retrieve all the information associated with a pet by issuing
a GET request to `/get-pet/<string:petname>`.

For example requesting `/get-pet/Dweble` might yield:

```
{
  "agility": 0.2,
  "experience": 0,
  "losses": 0,
  "name": "Dwebble",
  "senses": 0.3,
  "strength": 0.3,
  "wins": 0,
  "wit": 0.2
}
```

Or, if Dweble isn't in the databse it would yield "404 NOT FOUND" status code,
along with:

```JSON
{
  "message": "A pet with the name 'Dweble' does not exist."
}
```

### `[arena service]/arena`

You create a battle by issuing a POST to `/arena`.

An example POST looks like:

```JSON
{
  "name1": "Dweble",
  "name2": "Charmander",
  "category": "strength"
}
```

That post would create a battle between Dweble and Charmander: whoever
has the highest strength attribute wins. In the event of a tie,
whoever has more experience points wins. In the event of an experience tie,
the oldest pet wins.

The victor earns two experience points, and the 2nd-place pet
earns one experience point.

**Input JSON Schema**:

```JSON
{
    "type": "object",
    "properties": {
        "name1": {
            "type": "string"
        },
        "name2": {
            "type": "string"
        },
        "category": {
            "enum": ["strength", "agility", "wit", "senses"]
        }
    },
    "required": ["name1", "name2", "category"]
}
```

**Other possible responses**:

- If the POST does not contain valid JSON, `/arena` responds with 
  "400 BAD REQUEST" status code, along with
  `{"message": "No JSON object could be decoded"}`
- If the POST does not match the schema, `/arena` responds with
  "400 BAD REQUEST" status code, along with
  `{"message": "Your JSON post does not match CONTEST_SCHEMA.",
    "CONTEST_SCHEMA": ...
   }`
- If either (1) name1 == name2, or (2) one or more of the pets does not exist,
  then `/arena` responds with "400 BAD REQUEST" status code, along with
  `{"message": "One or more of the pets you specified do not exist, or
     you have specified that the same pet fight itself"}`.
   It would be preferable to give each of these cases unique error messages,
   rather then clumping them into one. However, I did not implement it that
   way to due to time constraints and it seems like a low priority change.


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
- Make sure pet names are url safe

TODO low priority
- Training interface: reports the most high value matches
- Leader board
