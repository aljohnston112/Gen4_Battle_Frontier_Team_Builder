from math import floor

from data_source.BattleFrontierPokemonDataSource import get_battle_frontier_pokemon
from data_source.PokemonDataSource import get_pokemon
from data_source.PokemonIndexDataSource import get_pokemon_name_to_index

pokemon_name_to_index = get_pokemon_name_to_index()
pokemon_index_to_pokemon = get_pokemon()
frontier_pokemon = get_battle_frontier_pokemon()


def get_attack_multiplier(nature: str):
    m = 1.0
    if nature in ["Lonely", "Brave", "Adamant", "Naughty"]:
        m = 1.1
    elif nature in ["Bold", "Timid", "Modest", "Calm"]:
        m = 0.9
    return m


def get_special_attack_multiplier(nature: str):
    m = 1.0
    if nature in ["Modest", "Mild", "Quiet", "Rash"]:
        m = 1.1
    elif nature in ["Adamant", "Impish", "Jolly", "Careful"]:
        m = 0.9
    return m


def get_defense_multiplier(nature: str):
    m = 1.0
    if nature in ["Bold", "Relaxed", "Impish", "Lax"]:
        m = 1.1
    elif nature in ["Lonely", "Hasty", "Mild", "Gentle"]:
        m = 0.9
    return m


def get_special_defense_multiplier(nature: str):
    m = 1.0
    if nature in ['Calm', 'Gentle', 'Sassy', "Careful"]:
        m = 1.1
    elif nature in ["Naughty", "Lax", "Naive", "Rash"]:
        m = 0.9
    return m


def get_speed_multiplier(nature):
    m = 1.0
    if nature in ["Timid", "Hasty", "Jolly", "Naive"]:
        m = 1.1
    elif nature in ["Brave", "Relaxed", "Quiet", "Sassy"]:
        m = 0.9
    return m


def get_iv_for_frontier_pokemon(set_number):
    return (set_number + 2) * 3


def get_hp_for_frontier_trainer(level, set_number, pokemon):
    pokemon_index = pokemon_name_to_index[pokemon['name']]
    base_health = pokemon_index_to_pokemon[pokemon_index].all_stats.base_stats.stats.health
    iv = get_iv_for_frontier_pokemon(set_number)
    assert pokemon["effort_values"][0]['stat_type'] == 'health'
    ev = pokemon["effort_values"][0]['value']
    hp = floor(((2.0 * base_health + iv + floor(ev / 4.0)) * level) / 100.0) + level + 10
    return hp


def get_stat_for_frontier_pokemon(base, iv, ev, level):
    return floor(((2.0 * base + iv + floor(ev / 4.0)) * level) / 100.0) + 5


def get_attack_for_frontier_pokemon(level, set_number, pokemon):
    pokemon_index = pokemon_name_to_index[pokemon['name']]
    base_attack = pokemon_index_to_pokemon[pokemon_index].all_stats.base_stats.stats.attack
    iv = get_iv_for_frontier_pokemon(set_number)
    assert pokemon["effort_values"][1]['stat_type'] == 'attack'
    ev = pokemon["effort_values"][1]['value']
    return floor(
        get_stat_for_frontier_pokemon(base_attack, iv, ev, level) *
        get_attack_multiplier(pokemon['nature'])
    )


def get_special_attack_for_frontier_pokemon(level, set_number, pokemon):
    pokemon_index = pokemon_name_to_index[pokemon['name']]
    base_attack = pokemon_index_to_pokemon[pokemon_index].all_stats.base_stats.stats.special_attack
    iv = get_iv_for_frontier_pokemon(set_number)
    assert pokemon["effort_values"][3]['stat_type'] == 'special_attack'
    ev = pokemon["effort_values"][3]['value']
    return floor(
        get_stat_for_frontier_pokemon(base_attack, iv, ev, level) *
        get_special_attack_multiplier(pokemon['nature'])
    )


def get_speed_for_frontier_trainer(level, set_number, pokemon):
    pokemon_index = pokemon_name_to_index[pokemon['name']]
    base_speed = pokemon_index_to_pokemon[pokemon_index].all_stats.base_stats.stats.speed
    iv = get_iv_for_frontier_pokemon(set_number)
    assert pokemon["effort_values"][5]['stat_type'] == 'speed'
    ev = pokemon["effort_values"][5]['value']
    return floor(
        get_stat_for_frontier_pokemon(base_speed, iv, ev, level) *
        get_speed_multiplier(pokemon['nature'])
    )


def get_defense_for_frontier_pokemon(level, set_number, pokemon):
    pokemon_index = pokemon_name_to_index[pokemon['name']]
    base_defense = pokemon_index_to_pokemon[pokemon_index].all_stats.base_stats.stats.defense
    iv = get_iv_for_frontier_pokemon(set_number)
    assert pokemon["effort_values"][2]['stat_type'] == 'defense'
    ev = pokemon["effort_values"][2]['value']
    return floor(
        get_stat_for_frontier_pokemon(base_defense, iv, ev, level) *
        get_defense_multiplier(pokemon['nature'])
    )


def get_special_defense_for_frontier_pokemon(level, set_number, pokemon):
    pokemon_index = pokemon_name_to_index[pokemon['name']]
    base_defense = pokemon_index_to_pokemon[pokemon_index].all_stats.base_stats.stats.special_defense
    iv = get_iv_for_frontier_pokemon(set_number)
    assert pokemon["effort_values"][4]['stat_type'] == 'special_defense'
    ev = pokemon["effort_values"][4]['value']
    return floor(
        get_stat_for_frontier_pokemon(base_defense, iv, ev, level) *
        get_special_defense_multiplier(pokemon['nature'])
    )

if __name__ == "__main__":
    level = 50
    pass


