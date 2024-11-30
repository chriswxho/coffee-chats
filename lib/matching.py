import logging
import random
from collections import defaultdict
from typing import Optional, List, Tuple, Dict
import networkx as nx
from networkx.exception import NetworkXError

logger = logging.getLogger(__name__)


def matchmake(
    ids: List[int], 
    constraints: Optional[List[Tuple[int, int]]] = None, 
) -> List[Tuple[int, int]]:
    # generate a undirected graph that connects each participant to every other
    G = nx.Graph()
    for idx in ids:
        G.add_node(idx)

    edges = []
    for i in range(len(ids)):
        for j in range(i+1, len(ids)):
            edges.append((ids[i], ids[j]))

    random.shuffle(edges) 
    
    for u, v in edges:
        G.add_edge(u, v)
    
    # exclude all edges according to constraints
    if constraints is not None:
        for constraint in constraints:
            try:
                G.remove_edge(*constraint)
            except NetworkXError:
                logger.debug(f"skip adding edge {constraint} because one or more persons in this pair is not a participant")

    matches = nx.max_weight_matching(G, maxcardinality=True)
    return matches

def get_all_pairing_history(
    schedules_of_pairings: Dict[str, List[Tuple[int, int]]]
) -> Dict[Tuple[int, int], List[str]]:
    """
    Consolidates all match histories.
    """
    seen: Dict[frozenset, List[str]] = defaultdict(list)
    for match_csv_filename, pairings in schedules_of_pairings.items():
        for pairing in pairings:
            pairing = frozenset(pairing)
            if pairing in seen:
                logger.debug(f"Pairing {pairing} was already done in {seen[pairing][-1]}")
            seen[pairing].append(match_csv_filename)
    
    formatted_seen = {}
    for k, v in seen.items():
        formatted_seen[tuple(k)] = v
    return formatted_seen
