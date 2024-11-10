import logging
import random
import math
from collections import defaultdict
from typing import Optional, List, Tuple, Dict
import networkx as nx

logger = logging.getLogger(__name__)


def matchmake(
    ids: List[int], 
    constraints: Optional[List[Tuple[int, int]]] = None, 
) -> List[Tuple[int, int]]:
    # generate a undirected graph that connects each participant to every other
    G = nx.Graph()
    for idx in ids:
        G.add_node(idx)

    for i in range(len(ids)):
        for j in range(i+1, len(ids)):
            G.add_edge(ids[i], ids[j])
    
    # exclude all edges according to constraints
    if constraints is not None:
        for constraint in constraints:
            try:
                G.remove_edge(*constraint)
            except nx.exception.NetworkXError:
                logger.debug(f"skip adding edge {constraint} because one or more persons in this pair is not a participant")

    matches = nx.max_weight_matching(G, maxcardinality=True)
    return matches

def check_pairing_history(
    schedules_of_pairings: Dict[str, List[Tuple[int, int]]]
) -> Dict[frozenset, List[str]]:
    """
    Consolidates all match histories.
    """
    seen: Dict[frozenset, List[str]] = defaultdict(list)
    for match_csv_filename, pairings in schedules_of_pairings.items():
        for pairing in pairings:
            pairing = frozenset(pairing)
            if pairing in seen:
                logger.warning(f"Pairing {pairing} was already done in {seen[pairing]}")
            seen[pairing].append(match_csv_filename)
    
    return seen
