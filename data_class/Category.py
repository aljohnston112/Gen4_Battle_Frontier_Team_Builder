from enum import unique, Enum


@unique
class Category(Enum):
    """
    Represents whether a Pokemon move of physical or special.
    """
    PHYSICAL = "physical"
    SPECIAL = "special"
    STATUS = "status"


__CATEGORY_DICT__ = {
    "physical": Category.PHYSICAL,
    "special": Category.SPECIAL,
    "other": Category.STATUS
}


def convert_to_attack_category(category):
    return __CATEGORY_DICT__[category.lower()]
