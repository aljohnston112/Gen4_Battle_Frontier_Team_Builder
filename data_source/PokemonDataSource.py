import urllib.request
from collections import defaultdict

from bs4 import BeautifulSoup, NavigableString

from data_class.Attack import Attack
from data_class.Category import convert_to_attack_category
from data_class.PokemonInformation import PokemonInformation
from data_class.PokemonType import convert_to_pokemon_type

base_url = "https://www.serebii.net/pokedex-dp/"
num_pokemon = 493


def get_url(index: int):
    return base_url + str(index).zfill(3) + ".shtml"


def __scrape_serebii_for_move_sets__():
    last_url_index = 0
    for pokemon_index in range(last_url_index + 1, num_pokemon + 1):
        url = get_url(pokemon_index)
        with urllib.request.urlopen(url) as fp:
            soup = BeautifulSoup(fp, 'html.parser')
            print()


if __name__ == "__main__":
    __scrape_serebii_for_move_sets__()
