pip install Flask
pip install jsonschema
pip install redis
pip install rq

wget http://download.redis.io/redis-stable.tar.gz
tar xvzf redis-stable.tar.gz
cd redis-stable
make
make install

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

TODO
- Hoist string constants somewhere else
- add more tests as needed
- breakup functions
- README
- Internal documentation
- Tool suite for production use
- Uncoil unnecessary test dependencies
- Training interface: reports the most high value matches
- Leader board
- History of past battles
- More interesting battles
- is None v. == None
- take testing off line
- check for valid petnames everywhere