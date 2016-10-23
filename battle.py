import time

# TODO: document
# TODO: does battle or contest update the db?

class BattlePet():

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

    result = {
        # Experience points
        category: 1
    }

    attr1 = pet1.attributes[category]
    attr2 = pet2.attributes[category]

    if attr1 > attr2:
        result["victor"] = pet1.name
    elif attr2 > attr1:
        result["victor"] = pet2.name
    else:
        # TODO
        pass

    return result


