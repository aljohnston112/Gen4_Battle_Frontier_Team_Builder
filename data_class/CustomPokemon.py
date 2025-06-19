from attr import dataclass

from data_class.PokemonType import PokemonType


@dataclass(frozen=True)
class CustomMove:
    name: str
    power: int
    move_type: PokemonType
    is_special: bool

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return (
                isinstance(other, CustomMove)
                and self.name == other.name
        )


@dataclass(hash=False)
class CustomPokemon:
    name: str
    hp: int
    attack: int
    special_attack: int
    defense: int
    special_defense: int
    speed: int
    types: list[PokemonType]
    moves: list[CustomMove]
    item: str

    def __hash__(self):
        return hash((
            self.name,
            tuple(sorted([m.name for m in self.moves])),
        ))

    def __eq__(self, other):
        return (
                isinstance(other, CustomPokemon)
                and self.name == other.name
                and sorted(m.name for m in self.moves) == sorted(
            m.name for m in other.moves)
        )