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
            tuple(sorted([m.name for m in self.moves])),
        ))

    def __eq__(self, other):
        return (
                isinstance(other, FrontierPokemon)
                and self.name == other.name
                and sorted(m.name for m in self.moves) == sorted(
            m.name for m in other.moves)
        )