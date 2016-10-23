import sqlite3
import time

# TODO: exceptions?
# TODO: document
# TODO: does battle or contest update the db?

SLEEP_TIME_BATTLE = 0.2


# Defined by argparse
# TODO: set to None
DB_FILENAME = "database.db"

class BattlePet():

    # TODO: take actual arguments in stead of pet_record
    def __init__(self, pet_record):
        self.name = pet_record[0]

        self.attributes = {
            "strength": pet_record[1],
            "agility": pet_record[2],
            "wit": pet_record[3],
            "senses": pet_record[4],
        }

        self.wins = pet_record[5]
        self.losses = pet_record[6]
        self.experience = pet_record[7]

def do_battle(pet1, pet2, category):

    time.sleep(SLEEP_TIME_BATTLE)

    result = {
        # Experience points
        category: 1
    }

    attr1 = pet1.attributes[category]
    attr2 = pet2.attributes[category]

    if attr1 > attr2:
        result["victor"] = pet1.name
        result["2nd place"] = pet2.name
    elif attr2 > attr1:
        result["victor"] = pet2.name
        result["2nd place"] = pet1.name
    else:
        # TODO
        result["victor"] = pet1.name
        result["2nd place"] = pet2.name
        pass

    return result

# TODO: document
def do_battle_db(pet1, pet2, category):
    result = do_battle(pet1, pet2, category)

    print result

    conn = sqlite3.connect(DB_FILENAME)

    print "asdf"

    #conn = get_db()
    print "asdf"
    cursor = conn.cursor()

    print result["victor"]

    cursor.execute('''
        UPDATE Pets SET wins = wins + 1 WHERE name = ?;
        ''',
        (result["victor"], ))

    cursor.execute('''
        UPDATE Pets SET losses = losses + 1 WHERE name = ?;
        ''',
        (result["2nd place"], ))

    cursor.execute('''
        UPDATE Pets SET experience = experience + 2 WHERE name = ?;
        ''',
        (result["victor"], ))

    cursor.execute('''
        UPDATE Pets SET experience = experience + 1 WHERE name = ?;
        ''',
        (result["2nd place"], ))

    conn.commit()

    conn.close()

    return result
