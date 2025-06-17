from enum import unique, Enum


@unique
class Category(Enum):
    """
    Represents whether a Pokémon move of physical or special.
    """
    PHYSICAL = "physical"
    SPECIAL = "special"
    STATUS = "status"


__CATEGORY_DICT__: dict[str, Category] = {
    Category.PHYSICAL.value: Category.PHYSICAL,
    Category.SPECIAL.value: Category.SPECIAL,
    Category.STATUS.value: Category.STATUS,
    "other": Category.STATUS
}


def convert_to_attack_category(category) -> Category:
    return __CATEGORY_DICT__[category.lower()]

if __name__ == '__main__':
    print(__CATEGORY_DICT__)