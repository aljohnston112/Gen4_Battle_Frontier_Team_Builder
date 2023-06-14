from attr import frozen


@frozen
class PokemonInformation:
    name: str
    id: int
    ability: str
    pounds: float
