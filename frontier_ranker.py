import itertools
import time
from itertools import combinations
from math import ceil

from Config import LEVEL
from data_class.Category import Category
from data_class.Nature import get_nature_multiplier, get_nature_enum
from data_class.SerebiiPokemon import SerebiiPokemon
from data_class.Stats import Stats
from data_source.FrontierPokemonDataSource import get_all_frontier_pokemon
from data_class.Move import Move
from data_class.PokemonType import PokemonType
from data_class.Stat import StatEnum, calculate_non_health_stat
from data_source.PokemonDataSource import get_all_serebii_pokemon
from data_source.PokemonIndexDataSource import get_pokemon_name_to_index
from data_source.TrainerSetDataSource import FrontierPokemon, TrainerSet, \
    get_frontier_pokemon
from data_source.move_data_source import get_move_map
from rank_searcher import filter_banned_pokemon, CustomPokemon, \
    convert_frontier_to_custom, calculate_survivability, \
    find_best_attack_against_target, combine_survivability_with_attack_results, \
    BattleResult

if __name__ == '__main__':
    all_serebii_pokemon: dict[int, SerebiiPokemon] = get_all_serebii_pokemon()
    pokemon_name_to_index: dict[str, int] = get_pokemon_name_to_index()
    all_serebii_pokemon: dict[int, SerebiiPokemon] = \
        filter_banned_pokemon(all_serebii_pokemon)

    # trainers_to_their_sets: dict[str, TrainerSet] = get_frontier_pokemon()
    # frontier_pokemon = set()
    # for trainer_set in trainers_to_their_sets.values():
    #         if 7 in trainer_set.set_numbers:
    #             for pokemon in trainer_set.pokemon:
    #                 frontier_pokemon.add(pokemon)

    frontier_pokemon = get_all_frontier_pokemon()

    move_map: dict[str, Move] = get_move_map()
    forces_to_be_reckoned_with: list[CustomPokemon] = []
    for pokemon_type in PokemonType:
        pokemon_type: PokemonType
        # power * relevant attack
        best_physical: tuple[int, Move, FrontierPokemon] | None = None
        best_special: tuple[int, Move, FrontierPokemon] | None = None
        for frontier_poke in frontier_pokemon:
            frontier_poke: FrontierPokemon
            frontier_poke_index = pokemon_name_to_index[frontier_poke.name]
            serebii_attacker = all_serebii_pokemon[frontier_poke_index]
            attacker_base_stats: Stats = \
                serebii_attacker.all_stats.base_stats.stats
            for attacker_move in frontier_poke.moves:
                attacker_move: Move
                if attacker_move.move_type == pokemon_type:
                    move_category = attacker_move.category
                    move_power: int = attacker_move.power
                    attacker_nature_enum = get_nature_enum(frontier_poke.nature)
                    if move_category == Category.PHYSICAL:
                        atk_ev: int = next(
                            (s.value for s in frontier_poke.effort_values
                             if s.stat_type == StatEnum.ATTACK)
                        )
                        attack: int = calculate_non_health_stat(
                            base=attacker_base_stats.attack,
                            iv=31,
                            ev=atk_ev,
                            level=LEVEL,
                            nature_multiplier=
                            get_nature_multiplier(
                                StatEnum.ATTACK,
                                attacker_nature_enum
                            )
                        )
                        p: int = move_power * attack
                        if best_physical is None:
                            best_physical: tuple[int, Move, FrontierPokemon] = \
                                (p, attacker_move, frontier_poke)
                        elif p > best_physical[0]:
                            best_physical: tuple[int, Move, FrontierPokemon] = \
                                (p, attacker_move, frontier_poke)
                    elif move_category == Category.SPECIAL:
                        sp_atk_ev: int = next(
                            (s.value for s in frontier_poke.effort_values
                             if s.stat_type == StatEnum.SPECIAL_ATTACK)
                        )
                        special_attack: int = calculate_non_health_stat(
                            base=attacker_base_stats.special_attack,
                            iv=31,
                            ev=sp_atk_ev,
                            level=LEVEL,
                            nature_multiplier=
                            get_nature_multiplier(
                                StatEnum.SPECIAL_ATTACK,
                                attacker_nature_enum
                            )
                        )
                        p: int = move_power * special_attack
                        if best_special is None:
                            best_special: tuple[int, Move, FrontierPokemon] = \
                                (p, attacker_move, frontier_poke)
                        elif p > best_special[0]:
                            best_special: tuple[int, Move, FrontierPokemon] = \
                                (p, attacker_move, frontier_poke)
        forces_to_be_reckoned_with.append(
            convert_frontier_to_custom(
                all_serebii_pokemon,
                100,
                best_physical[2],
                50
            )
        )
        forces_to_be_reckoned_with.append(
            convert_frontier_to_custom(
                all_serebii_pokemon,
                100,
                best_special[2],
                50
            )
        )

    pokemon_to_force_to_battle_results: \
        dict[str, dict[CustomPokemon, BattleResult]] = {}
    for force in forces_to_be_reckoned_with:
        force: CustomPokemon
        attacker_speed = force.speed

        survive_results: dict[str, float] = calculate_survivability(
            all_serebii_pokemon,
            force
        )
        attack_results: dict[str, tuple[str, float]] = \
            find_best_attack_against_target(all_serebii_pokemon, force)
        battle_results: dict[str, BattleResult] = \
            combine_survivability_with_attack_results(
                survive_results=survive_results,
                attack_results=attack_results
            )
        for defender_name, battle_result in battle_results.items():
            defender_name: str
            battle_result: BattleResult
            defender_speed = all_serebii_pokemon[
                pokemon_name_to_index[defender_name]
            ].all_stats.level_50_max_stats.speed
            if (ceil(battle_result.hits_given) < ceil(battle_result.hits_taken) or
                    (ceil(battle_result.hits_taken) == ceil(battle_result.hits_given) and
                    defender_speed > attacker_speed)
            ):
                if not pokemon_to_force_to_battle_results.get(defender_name):
                    pokemon_to_force_to_battle_results[defender_name] = {}
                pokemon_to_force_to_battle_results[defender_name][force] = \
                    battle_results[defender_name]

    battle_results_sorted = dict(sorted(
        pokemon_to_force_to_battle_results.items(),
        key=lambda x: (
            -len(x[1]),
            sum(br.hits_given / br.hits_taken for br in x[1].values())
        )
    ))

    cached_attacker_sets = {
        defender: set(battle_results_sorted[defender].keys())
        for defender in battle_results_sorted.keys()
    }

    p1 = [
        'Heatran', 'Lucario', 'Rampardos', 'Hariyama', 'Machamp',
        'Heracross', 'Breloom', 'Hitmonlee'
    ]

    p2 = [
        'Heatran', 'Arcanine', 'Gastrodon',
        'Camerupt', 'Houndoom', 'Magmar', 'Flareon', 'Garchomp', 'Donphan',
        'Rhydon', 'Mamoswine'
    ]

    p3 = list(battle_results_sorted.keys())
    for p in [
        "Regigigas", "Moltres", "Ho-oh", "Charizard", "Empoleon", "Swampert",
        "Infernape", "Latias", "Latios", "Blastoise", "Feraligatr", "Suicune",
        "Slaking", "Scizor", "Regice", "Gengar", "Registeel"
    ]:
        p3.remove(p)

    triples = [
        (a, b, c)
        for a, b, c in itertools.product(p1, p2, p3)
        if len({a, b, c}) == 3  # ensure all three are unique
    ]

    required_attackers = set([p for p in forces_to_be_reckoned_with if p.name not in ["Slaking", "Metagross"]])
    defender_keys = list(battle_results_sorted.keys())
    for defender_triple in triples:
        attacker_sets = \
            (cached_attacker_sets[defender] for defender in defender_triple)
        a, b, c = attacker_sets
        combined_attackers = a | b | c
        if combined_attackers >= required_attackers:
            print(defender_triple)
