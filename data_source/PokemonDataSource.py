import urllib.request

from bs4 import BeautifulSoup

base_url = "https://www.serebii.net/pokedex-dp/"
num_pokemon = 493
ms_delay = 500


def get_url(index: int):
    return base_url + str(index).zfill(3) + ".shtml"


def process_root(root):
    children = root.children
    for child in children:
        if child.name:
            pass


if __name__ == "__main__":
    last_url_index = 0
    for pokemon_index in range(last_url_index + 1, num_pokemon + 1):
        url = get_url(pokemon_index)
        with urllib.request.urlopen(url) as fp:
            soup = BeautifulSoup(fp, 'html.parser')
            process_root(soup.find('html'))
