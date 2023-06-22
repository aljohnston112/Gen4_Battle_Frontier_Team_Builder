import json

from Config import BATTLE_FRONTIER_SETS_FILE


def get_battle_frontier_pokemon():
    with open(BATTLE_FRONTIER_SETS_FILE, "r") as fo:
        return json.loads(fo.read())


if __name__ == "__main__":
    battle_frontier_pokemon = get_battle_frontier_pokemon()
    pass
