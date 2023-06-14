import urllib.request
from collections import defaultdict

from bs4 import BeautifulSoup

base_url = "https://www.serebii.net/pokedex-dp/"
num_pokemon = 493


def get_url(index: int):
    return base_url + str(index).zfill(3) + ".shtml"


def __scrape_serebii_for_move_sets():
    pokemon_to_moves = defaultdict(lambda: list())
    last_url_index = 0
    for pokemon_index in range(last_url_index + 1, num_pokemon + 1):
        url = get_url(pokemon_index)
        with urllib.request.urlopen(url) as fp:
            soup = BeautifulSoup(fp, 'html.parser')
            children = [c for c in soup.children]
            assert len(children) == 4
            html = children[3]
            assert html.name == "html"
            html_children = [c for c in html.children]
            assert len(html_children) == 5
            body = html_children[3]
            assert body.name == "body"
            body_children = [c for c in body.children]
            assert len(body_children) == 12
            wrapper = body_children[5]
            assert wrapper.name == "div"
            assert wrapper.attrs['id'] == "wrapper"
            wrapper_children = [c for c in wrapper.children]
            assert len(wrapper_children) == 13
            content = wrapper_children[9]
            assert content.name == "div"
            assert content.attrs['id'] == "content"
            content_children = [c for c in content.children]
            assert len(content_children) == 4
            main = content_children[3]
            assert main.name == "main"
            main_children = [c for c in main.children]
            assert len(main_children) == 2
            center = main_children[1]
            assert center['align'] == 'center'
            center_children = [c for c in center.children]
            assert len(center_children) == 6