pip install Flask
pip install jsonschema
pip install redis
pip install rq

wget http://download.redis.io/redis-stable.tar.gz
tar xvzf redis-stable.tar.gz
cd redis-stable
make

ERRATA:

- Never built a REST service before
- Unfamiliar with HTTP error codes, so I may be generating inappropriate
  errors
- Never used Flask or sqlite before
- Unfamiliar with conventions for git commit messages
- It's been about 12 years since I've used SQL
- It's been about 12 years since I've professionally coded in Python
- Unfamiliar with PEP 8 style
- Never used a job queue before
- No security built in
- Using polling instead of callbacks
