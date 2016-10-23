import sqlite3
import time

class BattlePet():

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

def do_battle(pet1, pet2, category, sleep_time_battle):

    time.sleep(sleep_time_battle)

    attr1 = pet1.attributes[category]
    attr2 = pet2.attributes[category]

    if attr1 > attr2:
        return (pet1.name, pet2.name)
    elif attr2 > attr1:
        return (pet2.name, pet1.name)

    # attr1 == attr2
    elif pet1.experience > pet2.experience:
        return (pet1.name, pet2.name)
    elif pet2.experience > pet1.experience:
        return (pet2.name, pet1.name)

    # pet1.experience == pet2.experience
    elif pet1.rowid < pet2.rowid:
        return (pet1.name, pet2.name)
    elif pet2.rowid < pet1.rowid:
        return (pet2.name, pet1.name)

    # This shouldn't happen
    else:
        assert pet1.rowid == pet2.rowid
        raise ValueError("pet1.rowid == pet2.rowid")

# TODO: document
# TODO: use with keyword to protect connection closing?
def do_battle_db(pet1, pet2, category, sleep_time_battle, db_filename):

    victor, second_place = do_battle(pet1, pet2, category, sleep_time_battle)

    conn = sqlite3.connect(db_filename)

    cursor = conn.cursor()

    cursor.execute('''
        UPDATE Pets SET wins = wins + 1 WHERE name = ?;
        ''',
        (victor, ))

    cursor.execute('''
        UPDATE Pets SET losses = losses + 1 WHERE name = ?;
        ''',
        (second_place, ))

    cursor.execute('''
        UPDATE Pets SET experience = experience + 2 WHERE name = ?;
        ''',
        (victor, ))

    cursor.execute('''
        UPDATE Pets SET experience = experience + 1 WHERE name = ?;
        ''',
        (second_place, ))

    conn.commit()

    conn.close()

    return victor
