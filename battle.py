import time

# TODO: does battle or contest update the db?

def petify(pet):
    return {
        "name": pet[0],
        "strength": pet[1],
        "agility": pet[2],
        "wit": pet[3],
        "senses": pet[4]
    }

def do_battle(pets, category):
    pet1 = petify(pets[0])
    pet2 = petify(pets[1])

    result = {
        # Experience points
        category: 1
    }

    if pet1[category] == pet2[category]:
        # TODO
        pass
    elif pet1[category] > pet2[category]:
        result["victor"] = pet1["name"]
    else:
        result["victor"] = pet2["name"]

    return result


