import math
from collections import defaultdict

from data_source.PokemonDataSource import get_pokemon
from data_source.PokemonRankDataSource import get_defense_multipliers_for_types


def calculate_stat(
        base: int,
        iv: int,
        ev: int,
        level: int,
        nature_multiplier: float
) -> int:
    stat = ((2 * base + iv + (ev // 4)) * level) // 100 + 5
    return math.floor(stat * nature_multiplier)


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


def calculate_gen4_damage(
        level: int,
        power: int,
        attack: int,
        defense: int,
        is_stab: bool,
        type_multiplier: float,
        random: float
) -> int:
    stab: float = 1.5 if is_stab else 1.0
    step1: int = math.floor(2 * level / 5) + 2
    step2: int = math.floor(step1 * power * attack / defense)
    step3: int = math.floor(step2 / 50) + 2
    damage: int = math.floor(
        math.floor(
            math.floor(
                step3 * random
            ) * stab
        ) * type_multiplier
    )
    return damage


def find_best_attack_against_target(
        all_pokemon: dict,
        o_stats: dict
):
    from math import inf

    o_hp = o_stats["hp"]
    o_defense = o_stats["defense"]
    o_special_defense = o_stats["special_defense"]
    o_types = frozenset(t.lower() for t in o_stats["types"])
    type_multipliers = get_defense_multipliers_for_types(o_types)

    results = []

    for pokemon in all_pokemon.values():
        min_stats = pokemon.all_stats.level_50_min_stats
        attack = min_stats.attack
        special_attack = min_stats.special_attack

        best_hits = inf
        best_move = None

        for move in get_all_attacks(pokemon, 50):
            bad_moves = {
                "selfdestruct", "gyro ball", "rock slide", "stone edge",
                "outrage", "iron tail", "focus blast", "dream eater", "spit up",
                "frustration", "thunder", "hydro pump", "blizzard", "explosion",
                "self-destruct", "flail", "reversal", "solarbeam", "hyper beam",
                "giga impact", "last resort", "focus punch", "fling",
                "grass knot", "magnitude"
            }
            if move.name.lower() in bad_moves or move.accuracy != 100:
                continue

            if move.power == 0:
                continue

            move_type = move.pokemon_type.name.lower()
            multiplier = type_multipliers[move_type]
            power = move.power
            is_special = move.category.name.lower() == "special"
            attack_stat = special_attack if is_special else attack
            defense_stat = o_special_defense if is_special else o_defense
            is_stab = move_type in [t.name.lower() for t in
                                    pokemon.pokemon_information.pokemon_types]

            damage: int = calculate_gen4_damage(
                level=50,
                power=power,
                attack=attack_stat,
                defense=defense_stat,
                is_stab=is_stab,
                type_multiplier=multiplier,
                random=0.85
            )
            hits = o_hp / damage if damage > 0 else inf

            if hits < best_hits:
                best_hits = hits
                best_move = move.name

        if best_move:
            results.append(
                (pokemon.pokemon_information.name, best_hits, best_move))

    results.sort(key=lambda x: x[1])
    return results


def get_all_attacks(pokemon, level: int) -> list:
    attacks = []

    for attack_level, attack_list in pokemon.level_to_attacks.items():
        if attack_level <= level:
            attacks.extend(attack_list)

    if pokemon.tm_or_hm_to_attack is not None:
        attacks.extend(pokemon.tm_or_hm_to_attack.values())

    if pokemon.egg_moves is not None:
        attacks.extend(pokemon.egg_moves)

    if pokemon.pre_evolution_index_to_level_to_moves is not None:
        for level_to_moves in pokemon.pre_evolution_index_to_level_to_moves.values():
            for attack_level, moves in level_to_moves.items():
                if attack_level <= level:
                    attacks.extend(moves)

    if pokemon.move_tutor_attacks is not None:
        attacks.extend(pokemon.move_tutor_attacks)

    if pokemon.game_to_level_to_moves is not None:
        for level_to_moves in pokemon.game_to_level_to_moves.values():
            for attack_level, move_list in level_to_moves.items():
                if attack_level <= level:
                    attacks.extend(move_list)

    if pokemon.special_moves is not None:
        attacks.extend(pokemon.special_moves)

    if pokemon.form_to_level_up_attacks is not None:
        for level_to_attacks in pokemon.form_to_level_up_attacks.values():
            for attack_level, attack_list in level_to_attacks.items():
                if attack_level <= level:
                    attacks.extend(attack_list)

    if pokemon.form_to_tm_or_hm_to_attack is not None:
        for moves_list in pokemon.form_to_tm_or_hm_to_attack.values():
            attacks.extend(moves_list.values())

    if pokemon.form_to_move_tutor_attacks is not None:
        for moves_list in pokemon.form_to_move_tutor_attacks.values():
            attacks.extend(moves_list)

    return attacks


def intersect_survivability(*results_lists):
    # results_lists: list of lists of (pokemon_name, hits_survived)
    survivability_map = defaultdict(list)

    # Record survivability per Pokémon per opponent
    for idx, results in enumerate(results_lists):
        for name, hits in results:
            survivability_map[name].append((idx, hits))

    # Filter Pokémon appearing in all lists
    filtered = {name: hits_list for name, hits_list in survivability_map.items()
                if len(hits_list) == len(results_lists)}

    # Format output: name -> list of hits survived per opponent
    output = []
    for name, hits_list in filtered.items():
        # Sort by opponent idx to keep order consistent
        hits_list.sort(key=lambda x: x[0])
        hits_values = [hits for _, hits in hits_list]
        output.append((name, hits_values))

    # Sort by minimum survivability (worst case) descending
    output.sort(key=lambda x: min(x[1]), reverse=True)
    return output


def calculate_survivability(
        pokemon_map,
        attacker_stats: dict,
        moves: list[tuple[int, str, bool]]  # (power, type, is_special)
):
    results = []

    o_special_attack = attacker_stats["special_attack"]
    o_attack = attacker_stats["attack"]
    o_types = set(t.lower() for t in attacker_stats["types"])

    for pokemon in pokemon_map.values():
        min_stats = pokemon.all_stats.level_50_min_stats
        hp = min_stats.health
        defense = min_stats.defense
        special_defense = min_stats.special_defense

        type_set = frozenset(
            t.name.lower() for t in pokemon.pokemon_information.pokemon_types)
        type_multipliers = get_defense_multipliers_for_types(type_set)

        # Calculate hits to survive for each move
        hits_list = []
        for power, move_type, is_special in moves:
            multiplier = type_multipliers.get(move_type, 1.0)
            is_stab = move_type in o_types

            # Choose relevant defense stat
            relevant_defense = special_defense if is_special else defense
            relevant_attack = o_special_attack if is_special else o_attack

            damage: int = calculate_gen4_damage(
                level=50,
                power=power,
                attack=relevant_attack,
                defense=relevant_defense,
                is_stab=is_stab,
                type_multiplier=multiplier,
                random=1.0
            )
            hits = hp / damage if damage > 0 else float("inf")
            hits_list.append(hits)

        # survivability is the worst case among moves
        survivability = min(hits_list)

        results.append((pokemon.pokemon_information.name, survivability))

    results.sort(key=lambda x: x[1], reverse=True)
    return results


BANNED_POKEMON_NAMES = {
    "Mewtwo", "Mew", "Lugia", "Ho-Oh", "Celebi", "Kyogre", "Groudon",
    "Rayquaza", "Jirachi", "Deoxys", "Dialga", "Palkia", "Giratina", "Phione",
    "Manaphy", "Darkrai", "Shaymin", "Arceus"
}


def filter_banned_pokemon(pokemon_map):
    return {
        idx: p for idx, p in pokemon_map.items()
        if p.pokemon_information.name not in BANNED_POKEMON_NAMES
    }


def main():
    pokemon_map = get_pokemon()
    pokemon_map = filter_banned_pokemon(pokemon_map)

    # Milotic
    # attacker_stats = {
    #     "hp": 202,
    #     "attack": 99,
    #     "special_attack": 167,
    #     "defense": 99,
    #     "special_defense": 145,
    #     "speed": 101,
    #     "types": ["water"]
    # }
    # moves = [
    #     (95, "water", True),  # Surf
    #     (95, "ice", True),  # Ice Beam
    # ]

    # Regigigas
    attacker_stats = {
        "hp": 217,
        "attack": 233,
        "special_attack": 90,
        "defense": 130,
        "special_defense": 130,
        "speed": 120,
        "types": ["normal"]
    }
    moves = [
        (121, "normal", False),  # Crush Grip
        (100, "ground", False),  # Earthquake
        (100, "rock", False),  # Stone Edge
        (75, "fighting", False),  # Drain Punch
    ]

    survive_results1 = calculate_survivability(pokemon_map, attacker_stats,
                                               moves)
    # for name, hits in survive_results1:
    #     print(f"{name} | Hits survived: {hits:.2f}")

    attack_results1 = find_best_attack_against_target(
        pokemon_map,
        attacker_stats
    )
    # for name, hits, move in attack_results1:
    #     print(f"{name} | Hits survived: {hits:.2f} | Move: {move}")

    # results = find_min_ev_for_hits(pokemon_map, attacker_stats)
    # print(f"{'Pokemon':<15} {'Hits':<8} {'EV':} {'Nature':} {'Move'}")
    # print("-" * 50)
    # for name, hits, ev, nature, move in results:
    #     nature_str = "Neutral" if nature == 1.0 else "Boosted"
    #     print(f"{name:<15} {hits:<8.2f} {ev:<5} {nature_str:<7} {move}")

    # Rhypherior
    # attacker_stats = {
    #     "hp": 190,
    #     "attack": 211,
    #     "defense": 182,
    #     "special_attack": 67,
    #     "special_defense": 75,
    #     "speed": 60,
    #     "types": ["ground", "rock"]
    # }
    # moves = [
    #     (100, "ground", False),  # Earthquake
    #     (80, "dark", False),  # Crunch
    #     (150, "rock", False)  # Rock Wrecker
    # ]

    # Heatran
    attacker_stats = {
        "hp": 166,
        "attack": 142,
        "special_attack": 200,
        "defense": 126,
        "special_defense": 126,
        "speed": 87,
        "types": ["fire", "steel"]
    }
    moves = [
        (100, "fire", True),  # Magma Storm
        (80, "steel", True),  # Flash Cannon
        (90, "ground", True),  # Earth Power
        (250, "normal", False),  # Explosion
    ]

    #
    survive_results2 = calculate_survivability(pokemon_map, attacker_stats,
                                               moves)
    # for name, hits in survive_results2:
    #     print(f"{name} | Hits survived: {hits:.2f}")

    attack_results2 = find_best_attack_against_target(
        pokemon_map,
        attacker_stats
    )
    # for name, hits, move in attack_results2:
    #     print(f"{name} | Hits survived: {hits:.2f} | Move: {move}")

    # dragonite
    # attacker_stats = {
    #     "hp": 166,
    #     "attack": 204,
    #     "defense": 115,
    #     "special_attack": 108,
    #     "special_defense": 152,
    #     "speed": 100,
    #     "types": ["dragon", "flying"]
    # }
    # moves = [
    #     (80, "dragon", False),  # Dragon Claw
    #     (60, "flying", False)  # Aerial Acs
    # ]

    # Cresselia
    attacker_stats = {
        "hp": 216,
        "attack": 81,
        "special_attack": 104,
        "defense": 161,
        "special_defense": 171,
        "speed": 105,
        "types": ["psychic"]
    }
    moves = [
        (90, "psychic", True),  # Psychic
        (90, "ice", True),  # Ice Beam
        (75, "bug", True),  # Signal Beam
    ]

    survive_results3 = calculate_survivability(pokemon_map, attacker_stats,
                                               moves)
    # for name, hits in survive_results3:
    #     print(f"{name} | Hits survived: {hits:.2f}")

    attack_results3 = find_best_attack_against_target(
        pokemon_map,
        attacker_stats
    )
    # for name, hits, move in attack_results3:
    #     print(f"{name} | Hits survived: {hits:<10.2f} | Move: {move}")

    survive_intersection = intersect_survivability(survive_results1,
                                                   survive_results2,
                                                   survive_results3)
    # for name, hits_list in survive_intersection:
    #     hits_str = " | ".join(f"{hits:.2f}" for hits in hits_list)
    #     print(f"{name} | Hits per opponent: {hits_str}")

    attack_intersection = intersect_attack_results(attack_results1,
                                                   attack_results2,
                                                   attack_results3)
    # for name, results in attack_intersection:
    #     print(f"{name}", end=" | ")
    #     for hits, move in results:
    #         print(f"{hits:.2f} ({move})", end=" | ")
    #     print()

    survival_map = {name: hits for name, hits in survive_intersection}
    attack_map = {name: results for name, results in attack_intersection}

    # Find common Pokémon
    shared_names = set(survival_map) & set(attack_map)

    for name in sorted(shared_names):
        hits_list = survival_map[name]
        attacks = attack_map[name]

        hits_str = " | ".join(f"{h:.2f}" for h in hits_list)
        attack_str = " | ".join(f"{h:.2f} ({m})" for h, m in attacks)

        print(f"{name} | Hits per opponent: {hits_str} | Attacks: {attack_str}")


if __name__ == '__main__':
    main()
