import math
import pprint
from collections import defaultdict

from battle_simulator import BattleResult, Hits
from damage_calculator import CustomPokemon, CustomMove, \
    find_best_attack_against_target, calculate_gen4_damage
from data_class.PokemonType import PokemonType
from data_class.SerebiiPokemon import SerebiiPokemon
from data_class.Stats import Stats
from data_source.PokemonDataSource import get_all_serebii_pokemon, \
    get_legal_serebii_pokemon
from data_source.TypeChartDataSource import get_defense_multipliers_for_types

slaking = CustomPokemon(
    name="Slaking",
    hp=257,
    attack=233,
    special_attack=103,
    defense=120,
    special_defense=85,
    speed=120,
    types=[PokemonType.NORMAL],
    moves=[
        CustomMove("Giga Impact", 150, PokemonType.NORMAL, False),
    ],
    item="choice band"
)

metagross = CustomPokemon(
    name="Metagross",
    hp=187,
    attack=205,
    special_attack=103,
    defense=150,
    special_defense=110,
    speed=90,
    types=[PokemonType.STEEL, PokemonType.PSYCHIC],
    moves=[
        CustomMove("Meteor Mash", 100, PokemonType.STEEL, False),
    ],
    item="choice band"
)

# Palmer's Pokemon

milotic = CustomPokemon(
    name="Milotic",
    hp=202,
    attack=99,
    special_attack=167,
    defense=99,
    special_defense=145,
    speed=101,
    types=[PokemonType.WATER],
    moves=[
        CustomMove("Surf", 95, PokemonType.WATER, True),
        CustomMove("Ice Beam", 95, PokemonType.ICE, True),
    ],
    item="shell bell"
)

rhyperior = CustomPokemon(
    name="Rhyperior",
    hp=190,
    attack=211,
    special_attack=67,
    defense=182,
    special_defense=75,
    speed=60,
    types=[PokemonType.GROUND, PokemonType.ROCK],
    moves=[
        CustomMove("Earthquake", 100, PokemonType.GROUND, False),
        CustomMove("Crunch", 80, PokemonType.DARK, False),
        CustomMove("Rock Wrecker", 150, PokemonType.ROCK, False),
    ],
    item="focus band"
)

dragonite = CustomPokemon(
    name="Dragonite",
    hp=166,
    attack=204,
    special_attack=108,
    defense=115,
    special_defense=152,
    speed=100,
    types=[PokemonType.DRAGON, PokemonType.FLYING],
    moves=[
        CustomMove("Dragon Claw", 80, PokemonType.DRAGON, False),
        CustomMove("Aerial Ace", 60, PokemonType.FLYING, False),
    ],
    item="lum berry"
)

regigigas = CustomPokemon(
    name="Regigigas",
    hp=217,
    attack=233,
    special_attack=90,
    defense=130,
    special_defense=130,
    speed=120,
    types=[PokemonType.NORMAL],
    moves=[
        CustomMove("Crush Grip", 121, PokemonType.NORMAL, False),
        CustomMove("Earthquake", 100, PokemonType.GROUND, False),
        CustomMove("Stone Edge", 100, PokemonType.ROCK, False),
        CustomMove("Drain Punch", 75, PokemonType.FIGHTING, False),
    ],
    item="brightpowder"
)

heatran = CustomPokemon(
    name="Heatran",
    hp=166,
    attack=142,
    special_attack=200,
    defense=126,
    special_defense=126,
    speed=87,
    types=[PokemonType.FIRE, PokemonType.STEEL],
    moves=[
        CustomMove("Magma Storm", 100, PokemonType.FIRE, True),
        CustomMove("Flash Cannon", 80, PokemonType.STEEL, True),
        CustomMove("Earth Power", 90, PokemonType.GROUND, True),
        CustomMove("Explosion", 250, PokemonType.NORMAL, False),
    ],
    item="focus sash"
)

cresselia = CustomPokemon(
    name="Cresselia",
    hp=216,
    attack=81,
    special_attack=104,
    defense=161,
    special_defense=171,
    speed=105,
    types=[PokemonType.PSYCHIC],
    moves=[
        CustomMove(PokemonType.PSYCHIC, 90, PokemonType.PSYCHIC, True),
        CustomMove("Ice Beam", 90, PokemonType.ICE, True),
        CustomMove("Signal Beam", 75, PokemonType.BUG, True),
    ],
    item="leftovers"
)

# Milotic Counters

abomasnow = CustomPokemon(
    name="Abomasnow",
    hp=150,
    attack=147,
    special_attack=87,
    defense=80,
    special_defense=90,
    speed=102,
    types=[PokemonType.GRASS, PokemonType.ICE],
    moves=[
        CustomMove("Wood Hammer", 120, PokemonType.GRASS, False),
    ],
    item=""
)

torterra = CustomPokemon(
    name="Torterra",
    hp=155,
    attack=147,
    special_attack=80,
    defense=110,
    special_defense=90,
    speed=102,
    types=[PokemonType.GRASS, PokemonType.GROUND],
    moves=[
        CustomMove("Wood Hammer", 120, PokemonType.GRASS, False),
    ],
    item=""
)

exeggutor = CustomPokemon(
    name="Exeggutor",
    hp=155,
    attack=147,
    special_attack=130,
    defense=81,
    special_defense=70,
    speed=102,
    types=[PokemonType.GRASS, PokemonType.PSYCHIC],
    moves=[
        CustomMove("Wood Hammer", math.floor(120 * 1.2), PokemonType.GRASS,
                   False),
        # Wood Hammer + Miracle Seed
    ],
    item="miracle seed"
)

electivire = CustomPokemon(
    name="Electivire",
    hp=135,
    attack=180,
    special_attack=90,
    defense=72,
    special_defense=90,
    speed=102,
    types=[PokemonType.ELECTRIC],
    moves=[
        CustomMove("Thunder Punch", math.floor(75 * 1.5), PokemonType.ELECTRIC,
                   False),
        # Thunder Punch + Life Orb
    ],
    item="life orb"
)

victreebel = CustomPokemon(
    name="Victreebel",
    hp=140,
    attack=163,
    special_attack=94,
    defense=70,
    special_defense=65,
    speed=102,
    types=[PokemonType.GRASS, "poison"],
    moves=[
        CustomMove("Leaf Blade", math.floor(90 * 1.2), PokemonType.GRASS,
                   False),
        # Leaf Blade + Miracle Seed
    ],
    item="miracle seed"
)

breloom = CustomPokemon(
    name="Breloom",
    hp=120,
    attack=183,
    special_attack=58,
    defense=85,
    special_defense=65,
    speed=102,
    types=[PokemonType.GRASS, "fighting"],
    moves=[
        CustomMove("Seed Bomb", math.floor(80 * 1.2), PokemonType.GRASS, False),
        # Seed Bomb + Miracle Seed
    ],
    item="miracle seed"
)

leafeon = CustomPokemon(
    name="Leafeon",
    hp=125,
    attack=169,
    special_attack=58,
    defense=135,
    special_defense=70,
    speed=102,
    types=[PokemonType.GRASS],
    moves=[
        CustomMove("Seed Bomb", math.floor(80 * 1.5), PokemonType.GRASS, False),
        # Seed Bomb + Life Orb
    ],
    item="life orb"
)


def intersect_attack_results(
        *results_lists: list[tuple[str, float, str]]
) -> list[tuple[str, list[tuple[float, str]]]]:
    """
    Given multiple result lists in the form (name, hits, move),
    return the intersection with their corresponding data from each list.
    """

    # Convert each result list to a dict for fast lookup
    name_to_results = [
        dict((name, (hits, move)) for name, hits, move in result_list)
        for result_list in results_lists]

    # Find common names across all result lists
    common_names = set(name_to_results[0])
    for d in name_to_results[1:]:
        common_names &= set(d)

    # Collect matching data from each list for those names
    intersection = []
    for name in sorted(common_names):
        per_list_data = [d[name] for d in name_to_results]
        intersection.append((name, per_list_data))

    return intersection


def intersect_survivability(*results_lists):
    survivability_map = defaultdict(list)

    for idx, results in enumerate(results_lists):
        for name, hits in results:
            survivability_map[name].append((idx, hits))

    filtered = {name: hits_list for name, hits_list in survivability_map.items()
                if len(hits_list) == len(results_lists)}

    output = []
    for name, hits_list in filtered.items():
        hits_list.sort(key=lambda x: x[0])
        hits_values = [hits for _, hits in hits_list]
        output.append((name, hits_values))

    output.sort(key=lambda x: min(x[1]), reverse=True)
    return output


def calculate_survivability(
        pokemon_map: dict[int, SerebiiPokemon],
        opponent: CustomPokemon,
) -> dict[str, float]:
    results: dict[str, float] = {}

    o_special_attack: int = opponent.special_attack
    o_attack: int = opponent.attack

    for pokemon in pokemon_map.values():
        pokemon: SerebiiPokemon
        min_stats: Stats = pokemon.all_stats.level_50_max_stats
        hp: int = min_stats.health
        defender_defense: int = min_stats.defense
        defender_special_defense: int = min_stats.special_defense
        defender_type_multipliers: dict[PokemonType, float] = \
            get_defense_multipliers_for_types(frozenset(opponent.types))

        # Calculate hits to survive for each move
        hits_list: list[float] = []
        for move in opponent.moves:
            move: CustomMove
            power: int = move.power
            move_type: PokemonType = move.move_type
            is_special: bool = move.is_special
            multiplier: float = defender_type_multipliers.get(
                move_type,
                1.0
            )
            is_stab: bool = move_type in opponent.types

            # Choose relevant defense stat
            relevant_defense: int = \
                defender_special_defense if is_special else defender_defense
            relevant_attack: int = \
                o_special_attack if is_special else o_attack

            damage: int = calculate_gen4_damage(
                power=power,
                attack=relevant_attack,
                defense=relevant_defense,
                is_stab=is_stab,
                type_multiplier=multiplier,
                random=1.0
            )
            hits: float = hp / damage if damage > 0 else float("inf")
            hits_list.append(hits)

        # survivability is the worst case among moves
        survivability = min(hits_list)
        results[pokemon.pokemon_information.name] = survivability
    return dict(sorted(results.items(), key=lambda x: -x[1]))




def combine_survivability_with_attack_results(
        survive_results: dict[str, float],
        attack_results: dict[str, tuple[CustomMove, float]]
):
    results: dict[str, BattleResult] = {}
    for name, survivability in survive_results.items():
        if name not in attack_results:
            continue
        attack_result = attack_results[name]
        results[name] = BattleResult(
            Hits(
                hits_taken=survivability,
                hits_given=attack_result[1]
            ),
            move=attack_result[0],
        )
    return dict(
        sorted(
            results.items(),
            key=lambda x: x[1].hits_given / x[1].hits_taken
        )
    )


def print_battle_results_against(p1, p2, p3, pokemon_map):
    survive_results1: dict[str, float] = calculate_survivability(pokemon_map,
                                                                 p1)
    attack_results1: dict[str, tuple[CustomMove, float]] = \
        find_best_attack_against_target(pokemon_map, p1)
    battle_results_1 = combine_survivability_with_attack_results(
        survive_results1,
        attack_results1
    )
    battle_results_1 = dict(
        {k: v for k, v, in battle_results_1.items() if v.hits.hits_given < 2.3})
    pprint.pp(battle_results_1)

    survive_results2 = calculate_survivability(pokemon_map, p2)
    attack_results2 = find_best_attack_against_target(pokemon_map, p2)
    battle_results_2 = combine_survivability_with_attack_results(
        survive_results2,
        attack_results2
    )
    battle_results_2 = dict({k: v for k, v, in battle_results_2.items() if
                             v.hits.hits_given < 2.3})
    pprint.pp(battle_results_2)
    # for name, survivability in battle_results_2.items():
    #     print(f"{name}")

    survive_results3 = calculate_survivability(pokemon_map, p3)
    attack_results3 = find_best_attack_against_target(pokemon_map, p3)
    battle_results_3 = combine_survivability_with_attack_results(
        survive_results3,
        attack_results3
    )
    battle_results_3 = dict(
        {k: v for k, v, in battle_results_3.items() if v.hits.hits_given < 2.3 * 2})
    # pprint.pp(battle_results_3)
    # for name, survivability in battle_results_3.items():
    #     print(f"{name}")

    # for name, survivability in battle_results_3.items():
    #     print(f"{name}")
    #
    # battle_results_2_and_3 = {}
    # for name, battle_result in battle_results_2.items():
    #     if name in battle_results_3:
    #         battle_results_2_and_3[name] = (battle_result, battle_results_3[name])
    # battle_results_2_and_3 = dict(sorted(battle_results_2_and_3.items(), key=lambda x: x[1][0].hits_given / x[1][0].hits_taken + x[1][1].hits_given / x[1][1].hits_taken))
    # pprint.pp(battle_results_2_and_3)

    # survive_intersection = intersect_survivability(
    #     survive_results1,
    #     survive_results2,
    #     survive_results3
    # )
    # attack_intersection = intersect_attack_results(
    #     attack_results1,
    #     attack_results2,
    #     attack_results3
    # )
    # survival_map = {name: hits for name, hits in survive_intersection}
    # attack_map = {name: results for name, results in attack_intersection}
    # # Find common Pokémon
    # shared_names = set(survival_map) & set(attack_map)
    # for name in sorted(shared_names):
    #     hits_list = survival_map[name]
    #     attacks = attack_map[name]
    #
    #     hits_str = " | ".join(f"{h:.2f}" for h in hits_list)
    #     attack_str = " | ".join(f"{h:.2f} ({m})" for h, m in attacks)
    #
    #     print(f"{name} | Hits per opponent: {hits_str} | Attacks: {attack_str}")


def print_battle_results_against_palmer_1(pokemon_map):
    p1 = slaking
    p2 = metagross
    p3 = dragonite
    print_battle_results_against(p1, p2, p3, pokemon_map)


def print_battle_results_against_palmer_2(pokemon_map):
    p1 = regigigas
    p2 = heatran
    p3 = cresselia
    print_battle_results_against(p1, p2, p3, pokemon_map)


def main():
    pokemon_map: dict[int, SerebiiPokemon] = get_legal_serebii_pokemon()

    print_battle_results_against_palmer_1(pokemon_map)
    # print_battle_results_against_palmer_2(pokemon_map)

    # pokemon_list = get_frontier_pokemon()
    #
    # set_map = defaultdict(list)
    # for trainer, sets_and_attackers in pokemon_list.items():
    #     set_numbers = sets_and_attackers[0]
    #     for set_number in set_numbers:
    #         set_map[set_number].append((trainer, sets_and_attackers[1]))

    # for set_number, trainers_and_attackers in set_map.items():
    #     for trainer, attackers in trainers_and_attackers:
    #         top_targets = {}
    #         for attacker in attackers:
    #             attacker_name = attacker.name
    #             attacker = convert_frontier_to_custom(pokemon_map, set_number, attacker, level=50)
    #             survivability = calculate_survivability(pokemon_map, attacker)
    #             attack_info = find_best_attack_against_target(pokemon_map, attacker)
    #             survivability.sort(key=lambda x: -x[1])
    #             top_targets[attacker_name] = survivability
    #         aggregate_hits = defaultdict(float)
    #
    #         for attacker, target_list in top_targets.items():
    #             for target_name, hits in target_list:
    #                 aggregate_hits[target_name] += hits
    #         sorted_aggregate = sorted(aggregate_hits.items(), key=lambda x: -x[1])
    #
    #         for defender, total_hits in sorted_aggregate[:10]:
    #             print(f"{defender}: {total_hits:.2f}")
    #         print()


if __name__ == '__main__':
    main()
