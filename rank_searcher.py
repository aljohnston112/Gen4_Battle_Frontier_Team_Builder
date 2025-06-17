import math
import pprint
from collections import defaultdict

from attr import dataclass

from data_class.Category import Category
from data_class.Move import Move
from data_class.Pokemon import Pokemon
from data_class.Stat import StatEnum, get_nature_multiplier, get_nature_enum, \
    calculate_non_health_stat, calculate_health_stat
from data_class.Stats import Stats
from data_source.PokemonDataSource import get_all_pokemon
from data_source.PokemonIndexDataSource import get_pokemon_name_to_index
from data_source.PokemonRankDataSource import get_defense_multipliers_for_types
from data_source.TrainerSetDataSource import FrontierPokemon


@dataclass
class CustomMove:
    power: int
    move_type: str
    is_special: bool


@dataclass
class CustomPokemon:
    name: str
    hp: int
    attack: int
    special_attack: int
    defense: int
    special_defense: int
    speed: int
    types: list[str]
    moves: list[CustomMove]
    item: str

# Palmer's Pokemon

milotic = CustomPokemon(
    name="Milotic",
    hp=202,
    attack=99,
    special_attack=167,
    defense=99,
    special_defense=145,
    speed=101,
    types=["water"],
    moves=[
        CustomMove(95, "water", True),  # Surf
        CustomMove(95, "ice", True),  # Ice Beam
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
    types=["ground", "rock"],
    moves=[
        CustomMove(100, "ground", False),  # Earthquake
        CustomMove(80, "dark", False),  # Crunch
        CustomMove(150, "rock", False),  # Rock Wrecker
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
    types=["dragon", "flying"],
    moves=[
        CustomMove(80, "dragon", False),  # Dragon Claw
        CustomMove(60, "flying", False),  # Aerial Ace
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
    types=["normal"],
    moves=[
        CustomMove(121, "normal", False),  # Crush Grip
        CustomMove(100, "ground", False),  # Earthquake
        CustomMove(100, "rock", False),  # Stone Edge
        CustomMove(75, "fighting", False),  # Drain Punch
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
    types=["fire", "steel"],
    moves=[
        CustomMove(100, "fire", True),  # Magma Storm
        CustomMove(80, "steel", True),  # Flash Cannon
        CustomMove(90, "ground", True),  # Earth Power
        CustomMove(250, "normal", False),  # Explosion
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
    types=["psychic"],
    moves=[
        CustomMove(90, "psychic", True),  # Psychic
        CustomMove(90, "ice", True),  # Ice Beam
        CustomMove(75, "bug", True),  # Signal Beam
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
    types=["grass", "ice"],
    moves=[
        CustomMove(120, "grass", False),  # Wood Hammer
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
    types=["grass", "ground"],
    moves=[
        CustomMove(120, "grass", False),  # Wood Hammer
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
    types=["grass", "psychic"],
    moves=[
        CustomMove(math.floor(120 * 1.2), "grass", False),  # Wood Hammer + Miracle Seed
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
    types=["electric"],
    moves=[
        CustomMove(math.floor(75 * 1.5), "electric", False),  # Thunder Punch + Life Orb
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
    types=["grass", "poison"],
    moves=[
        CustomMove(math.floor(90 * 1.2), "grass", False),  # Leaf Blade + Miracle Seed
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
    types=["grass", "fighting"],
    moves=[
        CustomMove(math.floor(80 * 1.2), "grass", False),  # Seed Bomb + Miracle Seed
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
    types=["grass"],
    moves=[
        CustomMove(math.floor(80 * 1.5), "grass", False),  # Seed Bomb + Life Orb
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
        opponent: CustomPokemon
) -> dict[str, tuple[str, float]]:
    from math import inf

    o_hp: int = opponent.hp
    o_defense: int = opponent.defense
    o_special_defense: int = opponent.special_defense
    o_types: frozenset[str] = frozenset(t.lower() for t in opponent.types)
    o_type_multipliers: dict[str, float] = \
        get_defense_multipliers_for_types(o_types)

    results: dict[str, tuple[str, float]] = {}
    for pokemon in all_pokemon.values():
        pokemon: Pokemon
        min_stats: Stats = pokemon.all_stats.level_50_min_stats
        attack: int = min_stats.attack
        special_attack: int = min_stats.special_attack

        best_hits: float = inf
        best_move: str | None = None

        for move in get_all_attacks(pokemon, 50):
            move: Move
            bad_moves = {
                "selfdestruct", "gyro ball", "rock slide", "stone edge",
                "outrage", "iron tail", "focus blast", "dream eater", "spit up",
                "frustration", "thunder", "hydro pump", "blizzard", "explosion",
                "self-destruct", "flail", "reversal", "solarbeam", "hyper beam",
                "giga impact", "last resort", "focus punch", "fling",
                "grass knot", "magnitude", "low kick", "dig"
            }
            if move.name.lower() in bad_moves or move.accuracy != 100:
                continue

            if move.power == 0:
                continue

            move_type: str = move.move_type.name.lower()
            multiplier: float = o_type_multipliers[move_type]
            power: int = move.power
            is_special: bool = move.category.name.lower() == "special"
            attack_stat: int = special_attack if is_special else attack
            defense_stat: int = o_special_defense if is_special else o_defense
            is_stab: bool = move_type in [
                t.name.lower()
                for t in pokemon.pokemon_information.pokemon_types
            ]

            damage: int = calculate_gen4_damage(
                level=50,
                power=power,
                attack=attack_stat,
                defense=defense_stat,
                is_stab=is_stab,
                type_multiplier=multiplier,
                random=0.85
            )
            hits: float = o_hp / damage if damage > 0 else inf

            if hits < best_hits:
                best_hits: float = hits
                best_move: str = move.name

        if best_move:
            results[pokemon.pokemon_information.name] = (best_move, best_hits)

    return dict(sorted(results.items(), key=lambda x: x[1][1]))


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
        pokemon_map: dict[str, Pokemon],
        opponent: CustomPokemon,
) -> dict[str, float]:
    results: dict[str, float] = {}

    o_special_attack: int = opponent.special_attack
    o_attack: int = opponent.attack
    o_types: set[str] = set(t.lower() for t in opponent.types)

    for pokemon in pokemon_map.values():
        pokemon: Pokemon
        min_stats: Stats = pokemon.all_stats.level_50_min_stats
        hp: int = min_stats.health
        defender_defense: int = min_stats.defense
        defender_special_defense: int = min_stats.special_defense

        defender_type_set: frozenset[str] = frozenset(
            t.name.lower() for t in pokemon.pokemon_information.pokemon_types
        )
        defender_type_multipliers: dict[str, float] = \
            get_defense_multipliers_for_types(defender_type_set)

        # Calculate hits to survive for each move
        hits_list: list[float] = []
        for move in opponent.moves:
            move: CustomMove
            power: int = move.power
            move_type: str = move.move_type
            is_special: bool = move.is_special
            multiplier: float = defender_type_multipliers.get(move_type, 1.0)
            is_stab: bool = move_type in o_types

            # Choose relevant defense stat
            relevant_defense: int = \
                defender_special_defense if is_special else defender_defense
            relevant_attack: int = \
                o_special_attack if is_special else o_attack

            damage: int = calculate_gen4_damage(
                level=50,
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


@dataclass
class BattleResult:
    name: str
    hits_taken: float
    hits_given: float
    move: str


def combine_survivability_with_attack_results(
        survive_results: dict[str,float],
        attack_results: dict[str, tuple[str, float]]
):
    results: dict[str, BattleResult] = {}
    for name, survivability in survive_results.items():
        if name not in attack_results:
            continue
        attack_result = attack_results[name]
        results[name] = BattleResult(
            name=name,
            hits_taken=survivability,
            hits_given=attack_result[1],
            move=attack_result[0],
        )
    return dict(sorted(results.items(), key=lambda x: x[1].hits_given / x[1].hits_taken))


def print_battle_results_against(p1, p2, p3, pokemon_map):
    # survive_results1:dict[str, float] = calculate_survivability(pokemon_map, p1)
    # attack_results1: dict[str, tuple[str, float]] = \
    #     find_best_attack_against_target(pokemon_map, p1)
    # battle_results_1 = combine_survivability_with_attack_results(
    #     survive_results1,
    #     attack_results1
    # )
    # battle_results_1 = dict({k: v for k, v, in battle_results_1.items() if v.hits_given < 2.3})
    # # pprint.pp(battle_results_1)
    #
    survive_results2 = calculate_survivability(pokemon_map, p2)
    attack_results2 = find_best_attack_against_target(pokemon_map, p2)
    battle_results_2 = combine_survivability_with_attack_results(
        survive_results2,
        attack_results2
    )
    battle_results_2 = dict({k: v for k, v, in battle_results_2.items() if v.hits_given < (2.3 * 2 / 1.5)})
    pprint.pp(battle_results_2)
    # for name, survivability in battle_results_2.items():
    #     print(f"{name}")


    survive_results3 = calculate_survivability(pokemon_map, p3)
    attack_results3 = find_best_attack_against_target(pokemon_map, p3)
    battle_results_3 = combine_survivability_with_attack_results(
        survive_results3,
        attack_results3
    )
    battle_results_3 = dict({k: v for k, v, in battle_results_3.items() if v.hits_given < 2.3 * 2})
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
    p1 = milotic
    p2 = rhyperior
    p3 = dragonite
    print_battle_results_against(p1, p2, p3, pokemon_map)


def print_battle_results_against_palmer_2(pokemon_map):
    p1 = regigigas
    p2 = heatran
    p3 = cresselia
    print_battle_results_against(p1, p2, p3, pokemon_map)


pokemon_to_index = get_pokemon_name_to_index()


def convert_frontier_to_custom(
        pokemon_map: dict[int, Pokemon],
        set_number: int,
        frontier: FrontierPokemon,
        level: int
) -> CustomPokemon:
    custom_moves = [
        CustomMove(
            power=move.power,
            move_type=move.move_type.name.lower(),
            is_special=(move.category == Category.SPECIAL),
        )
        for move in frontier.moves
    ]

    pokemon: Pokemon = pokemon_map[pokemon_to_index[frontier.name]]
    base_stats = pokemon.all_stats.base_stats.stats
    iv = (set_number + 1) * 3
    iv = min(iv, 31)
    hp_ev = next((s.value for s in frontier.effort_values if
                  s.stat_type == StatEnum.HEALTH))
    hp = calculate_health_stat(
        base=base_stats.health,
        iv=iv,
        ev=hp_ev,
        level=level
    )

    atk_ev = next((s.value for s in frontier.effort_values if
                   s.stat_type == StatEnum.ATTACK))
    attack = calculate_non_health_stat(
        base=base_stats.attack,
        iv=iv,
        ev=atk_ev,
        level=level,
        nature_multiplier=
        get_nature_multiplier(StatEnum.ATTACK, get_nature_enum(frontier.nature))
    )

    sp_atk_ev = next((s.value for s in frontier.effort_values if
                      s.stat_type == StatEnum.SPECIAL_ATTACK))
    special_attack = calculate_non_health_stat(
        base=base_stats.special_attack,
        iv=iv,
        ev=sp_atk_ev,
        level=level,
        nature_multiplier=
        get_nature_multiplier(StatEnum.SPECIAL_ATTACK,
                              get_nature_enum(frontier.nature))
    )

    def_ev = next((s.value for s in frontier.effort_values if
                   s.stat_type == StatEnum.DEFENSE))
    defense = calculate_non_health_stat(
        base=base_stats.defense,
        iv=iv,
        ev=def_ev,
        level=level,
        nature_multiplier=
        get_nature_multiplier(StatEnum.DEFENSE,
                              get_nature_enum(frontier.nature))
    )

    sp_def_ev = next((s.value for s in frontier.effort_values if
                      s.stat_type == StatEnum.SPECIAL_DEFENSE))
    special_defense = calculate_non_health_stat(
        base=base_stats.special_defense,
        iv=iv,
        ev=sp_def_ev,
        level=level,
        nature_multiplier=
        get_nature_multiplier(StatEnum.SPECIAL_DEFENSE,
                              get_nature_enum(frontier.nature))
    )

    speed_ev = next((s.value for s in frontier.effort_values if
                     s.stat_type == StatEnum.SPEED))
    speed = calculate_non_health_stat(
        base=base_stats.speed,
        iv=iv,
        ev=speed_ev,
        level=level,
        nature_multiplier=
        get_nature_multiplier(StatEnum.SPEED, get_nature_enum(frontier.nature))
    )

    return CustomPokemon(
        name=pokemon.pokemon_information.name,
        hp=hp,
        attack=attack,
        special_attack=special_attack,
        defense=defense,
        special_defense=special_defense,
        speed=speed,
        types=[t.name.lower() for t in frontier.types],
        moves=custom_moves,
        item=frontier.item
    )


def main():
    pokemon_map = get_all_pokemon()
    pokemon_map = filter_banned_pokemon(pokemon_map)

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
