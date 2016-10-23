#/usr/bin/env bash
#
# To setup for the test exectue the following commands first:
#
#   $ redis-server
#   $ rq worker
#   $ python management.py
#   $ python arena.py
#

rm database.db
python db.py

# Populate the database with pets
./new_pet.py --name Abra       --strength 0.2 --agility 0.2 --wit 0.3 --senses 0.3
./new_pet.py --name Blissey    --strength 0.1 --agility 0.2 --wit 0.4 --senses 0.3
./new_pet.py --name Charmander --strength 0.5 --agility 0.0 --wit 0.3 --senses 0.2
./new_pet.py --name Dwebble    --strength 0.3 --agility 0.2 --wit 0.2 --senses 0.3
./new_pet.py --name Flygon     --strength 0.6 --agility 0.1 --wit 0.1 --senses 0.2

# Fails because attribute sums is > 1.0
./new_pet.py --name Failure     --strength 2.0 --agility 0.1 --wit 0.1 --senses 0.2 --expect_400

# Fails because Charmander already exists
./new_pet.py --name Charmander --strength 0.5 --agility 0.0 --wit 0.3 --senses 0.2 --expect_400

./get_pet.py --name Dwebble 

./get_pet.py --name Failure --expect_404 
