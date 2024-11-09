import random
import math
from typing import List, Tuple


def matching(ids: List[int], constraints: List[Tuple[int, int]] = [], preferences: List[Tuple[int, int]] = []):
    # generate a fully connected graph that connects all ids
    g = {
        frozenset({ids[i], ids[j]}) for i in range(len(ids)) for j in range(len(ids)) if i != j
    }

    # exclude negative matches (constraints)
    g.pop(frozenset({2, 3}))

    # honor preferences
    print(g)


matching(list(range(5)))
