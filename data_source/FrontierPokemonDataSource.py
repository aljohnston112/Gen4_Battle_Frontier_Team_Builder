import pprint

from data_source.TrainerSetDataSource import FrontierPokemon, \
    get_frontier_pokemon, TrainerSet


def get_all_frontier_pokemon() -> set[FrontierPokemon]:
    trainers_to_their_sets: dict[str, TrainerSet] = \
        get_frontier_pokemon()
    all_frontier_pokemon: set[FrontierPokemon] = set()
    for trainer_names, trainer_set in trainers_to_their_sets.items():
        trainer_names: str
        trainer_set: TrainerSet
        pokemon_set: set[FrontierPokemon] = trainer_set.pokemon
        all_frontier_pokemon.update(pokemon_set)
    return all_frontier_pokemon

if __name__ == '__main__':
    g_all_frontier_pokemon: set[FrontierPokemon] = get_all_frontier_pokemon()
    pprint.pprint(g_all_frontier_pokemon)
