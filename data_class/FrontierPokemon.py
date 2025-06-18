import attr

from data_class.Move import Move
from data_class.PokemonType import PokemonType
from data_class.Stat import Stat


@attr.define(frozen=True, hash=False)
class FrontierPokemon:
    name: str
    nature: str
    types: list[PokemonType]
    item: str
    moves: list[Move]
    effort_values: list[Stat]
    set_numbers: list[int]

    def __hash__(self):
        return hash((
            self.name,
            tuple(self.set_numbers),
            tuple(self.moves),
        ))