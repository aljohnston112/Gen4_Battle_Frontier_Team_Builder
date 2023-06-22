import json
from collections import defaultdict
from math import floor
from os.path import exists
from typing import Dict

import cattr

from Config import SET_TO_POKEMON_TO_DAMAGE_TABLES
from data_class.AttackDamageTable import AttackDamageTable, AttackDamageTables
from data_class.PokemonType import convert_to_pokemon_type
from data_source.BattleFrontierPokemonDataSource import get_battle_frontier_pokemon
from data_source.PokemonDataSource import get_pokemon
from data_source.PokemonIndexDataSource import get_pokemon_name_to_index

pokemon_name_to_index = get_pokemon_name_to_index()
pokemon_index_to_pokemon = get_pokemon()
frontier_pokemon = get_battle_frontier_pokemon()

frontier_set_to_pokemon_to_move_damage = defaultdict()


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


def get_set_to_damage_tables(level):
    set_number_to_damage_table = defaultdict(lambda: [])
    for set_number, pokemon_list in frontier_pokemon.items():
        for pokemon in pokemon_list:
            damage_tables = []
            hp = get_hp_for_frontier_trainer(level, int(set_number), pokemon)
            speed = get_speed_for_frontier_trainer(level, int(set_number), pokemon)
            attack = get_attack_for_frontier_pokemon(level, int(set_number), pokemon)
            special_attack = get_special_attack_for_frontier_pokemon(level, int(set_number), pokemon)

            defense = get_defense_for_frontier_pokemon(level, int(set_number), pokemon)
            special_defense = get_special_defense_for_frontier_pokemon(level, int(set_number), pokemon)
            min_defense = 5
            max_defense = 230
            for move in pokemon['moves']:
                move_type = move['move_type']
                power = move['power']
                category = move['category']
                if category != "status":
                    a = attack if category == "physical" else special_attack
                    defense_to_health = dict()
                    x = (((2.0 * level) / 5.0) + 2) * power * a
                    for d in range(min_defense, max_defense + 1):
                        damage = ((x / d) / 50.0) + 2
                        if move_type.lower() in pokemon['types']:
                            damage *= 1.5
                        defense_to_health[d] = damage
                    damage_table = AttackDamageTable(
                        attack_name=move['name'],
                        move_type=move["move_type"],
                        category=move["category"],
                        defense_to_damage=defense_to_health
                    )
                    damage_tables.append(damage_table)
            set_number_to_damage_table[set_number].append(
                AttackDamageTables(
                    pokemon=pokemon['name'],
                    pokemon_types=[convert_to_pokemon_type(t) for t in pokemon["types"]],
                    hp=hp,
                    defense=defense,
                    special_defense=special_defense,
                    speed=speed,
                    attack_damage_tables=damage_tables
                )
            )
    return set_number_to_damage_table


def load_frontier_set_to_damage_tables(level) -> Dict[int, AttackDamageTables]:
    file_name = SET_TO_POKEMON_TO_DAMAGE_TABLES + str(level)
    if not exists(file_name):
        set_to_damage_tables = get_set_to_damage_tables(level)
        with open(file_name, "w") as fo:
            fo.write(json.dumps(cattr.unstructure(set_to_damage_tables)))
    else:
        with open(file_name, "r") as fo:
            set_to_damage_tables = cattr.structure(json.loads(fo.read()),  Dict[str, list[AttackDamageTables]])
    return set_to_damage_tables


if __name__ == "__main__":
    level = 50
    set_to_damage_tables = load_frontier_set_to_damage_tables(level)
    pass


