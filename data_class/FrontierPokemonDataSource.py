from collections import defaultdict

from data_source.TrainerSetDataSource import FrontierPokemon, \
    get_frontier_pokemon


def get_all_frontier_pokemon() -> set[FrontierPokemon]:
    trainers_to_set_numbers_and_pokemon: \
        defaultdict[str, tuple[list[int], set[FrontierPokemon]]] = \
        get_frontier_pokemon()
    all_frontier_pokemon: set[FrontierPokemon] = set()
    for trainer_names, set_number_set_and_pokemon_set_tuple \
            in trainers_to_set_numbers_and_pokemon.items():
        trainer_names: str
        set_number_set_and_pokemon_set_tuple: \
            tuple[FrontierPokemon, set[FrontierPokemon]]
        pokemon_set: set[FrontierPokemon] = \
            set_number_set_and_pokemon_set_tuple[1]
        all_frontier_pokemon.update(pokemon_set)
    return all_frontier_pokemon