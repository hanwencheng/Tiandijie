import random
from typing import List


def random_select(target_list: List, num: int):
    return random.sample(target_list, min(len(target_list), num))
