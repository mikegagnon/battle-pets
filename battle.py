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
    def __init__(self, name, strength, agility, wit, senses, wins, losses,
            experience, rowid):

        self.name = name

        self.attributes = {
            "strength": strength,
            "agility": agility,
            "wit": wit,
            "senses": senses,
        }

        self.wins = wins
        self.losses = losses
        self.experience = experience
        self.rowid = rowid

def do_battle(pet1, pet2, category):

    time.sleep(SLEEP_TIME_BATTLE)

    result = {}

    attr1 = pet1.attributes[category]
    attr2 = pet2.attributes[category]

    if attr1 > attr2:
        result["victor"] = pet1.name
        result["2nd place"] = pet2.name
    elif attr2 > attr1:
        result["victor"] = pet2.name
        result["2nd place"] = pet1.name

    # attr1 == attr2
    elif pet1.experience > pet2.experience:
        result["victor"] = pet1.name
        result["2nd place"] = pet2.name
    elif pet2.experience > pet1.experience:
        result["victor"] = pet2.name
        result["2nd place"] = pet1.name

    # pet1.experience == pet2.experience
    elif pet1.rowid < pet2.rowid:
        result["victor"] = pet1.name
        result["2nd place"] = pet2.name
    elif pet2.rowid < pet1.rowid:
        result["victor"] = pet2.name
        result["2nd place"] = pet1.name

    # This shouldn't happen
    else:
        assert pet1.rowid == pet2.rowid
        raise ValueError("pet1.rowid == pet2.rowid")

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
