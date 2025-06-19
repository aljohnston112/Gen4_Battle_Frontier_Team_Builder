from typing import Optional

from attr import frozen

from data_class.Category import Category
from data_class.PokemonType import PokemonType


@frozen
class Move:
    name: str
    move_type: PokemonType
    category: Category
    power: int
    accuracy: int
    effect_percent: Optional[int] = None