import random
import math
from typing import Optional, List, Tuple


def matchmake(
    ids: List[int], 
    constraints: Optional[List[Tuple[int, int]]] = None, 
    preferences: Optional[List[Tuple[int, int]]] = None,
) -> List[Tuple[int, int]]:
    # generate a fully connected graph that connects all ids
    g = {
        frozenset({ids[i], ids[j]}) for i in range(len(ids)) for j in range(len(ids)) if i != j
    }

    # exclude negative matches (constraints)
    # g.remove(frozenset({2, 3}))

    # honor preferences
    return [(u,v) for u,v in g]
