from pprint import pp

from data_class.Category import Category
from data_class.FrontierPokemonDataSource import get_all_frontier_pokemon
from data_class.Move import Move
from data_class.PokemonType import PokemonType
from data_class.Stat import StatEnum, calculate_non_health_stat, \
    get_nature_multiplier, get_nature_enum
from data_source.PokemonDataSource import get_all_pokemon
from data_source.PokemonIndexDataSource import get_pokemon_name_to_index
from data_source.TrainerSetDataSource import FrontierPokemon
from data_source.move_data_source import get_move_map
from rank_searcher import filter_banned_pokemon, CustomPokemon, \
    convert_frontier_to_custom, calculate_survivability, \
    find_best_attack_against_target, combine_survivability_with_attack_results

if __name__ == '__main__':
    pokemon_map = get_all_pokemon()
    pokemon_to_index = get_pokemon_name_to_index()
    pokemon_map = filter_banned_pokemon(pokemon_map)

    frontier_pokemon: set[FrontierPokemon] = get_all_frontier_pokemon()
    move_map: dict[str, Move] = get_move_map()
    forces_to_be_reckoned_with: list[CustomPokemon] = []
    for pokemon_type in PokemonType:

        best_physical: tuple[int, Move, FrontierPokemon] | None = None
        best_special: tuple[int, Move, FrontierPokemon] | None = None
        for pokemon in frontier_pokemon:
            base_stats = pokemon_map[
                pokemon_to_index[pokemon.name]].all_stats.base_stats.stats
            for move in pokemon.moves:
                if move.move_type == pokemon_type:
                    if move.category == Category.PHYSICAL:
                        atk_ev = next(
                            (s.value for s in pokemon.effort_values if
                             s.stat_type == StatEnum.ATTACK))
                        attack = calculate_non_health_stat(
                            base=base_stats.attack,
                            iv=31,
                            ev=atk_ev,
                            level=50,
                            nature_multiplier=
                            get_nature_multiplier(
                                StatEnum.ATTACK,
                                get_nature_enum(pokemon.nature)
                            )
                        )
                        p = move.power * attack
                        if best_physical is None:
                            best_physical = (p, move, pokemon)
                        elif p > best_physical[0]:
                            best_physical = (p, move, pokemon)
                    elif move.category == Category.SPECIAL:
                        sp_atk_ev = next(
                            (s.value for s in pokemon.effort_values if
                             s.stat_type == StatEnum.SPECIAL_ATTACK))
                        special_attack = calculate_non_health_stat(
                            base=base_stats.special_attack,
                            iv=31,
                            ev=sp_atk_ev,
                            level=50,
                            nature_multiplier=
                            get_nature_multiplier(
                                StatEnum.SPECIAL_ATTACK,
                                get_nature_enum(pokemon.nature)
                            )
                        )
                        p = move.power * special_attack
                        if best_special is None:
                            best_special = (p, move, pokemon)
                        elif p > best_special[0]:
                            best_special = (p, move, pokemon)
        forces_to_be_reckoned_with.append(
            convert_frontier_to_custom(
                pokemon_map,
                100,
                best_physical[2],
                50
            )
        )
        forces_to_be_reckoned_with.append(
            convert_frontier_to_custom(
                pokemon_map,
                100,
                best_special[2],
                50
            )
        )
    # battle_results_1 = dict({k: v for k, v, in battle_results_1.items() if v.hits_given < 2.3})
    # pp(aggregated_battle_results)

    aggregated_battle_results = {}
    for force in forces_to_be_reckoned_with[1:]:
        survive_results: dict[str, float] = calculate_survivability(
            pokemon_map, force)
        attack_results: dict[str, tuple[str, float]] = \
            find_best_attack_against_target(pokemon_map, force)
        battle_results = combine_survivability_with_attack_results(
            survive_results,
            attack_results
        )
        for name, battle_result in battle_results.items():
            if name not in aggregated_battle_results:
                aggregated_battle_results[name] = ()
            aggregated_battle_results[name] += (battle_results[name],)

    battle_results_sorted = dict(sorted(
        aggregated_battle_results.items(),
        key=lambda x: sum(br.hits_given / br.hits_taken for br in x[1])
    ))
    pp(aggregated_battle_results)

