import os
import csv
import datetime
from typing import Dict, List, Tuple

PAIRINGS_LOCATION = "pairings"
IDS_LOCATION = "ids"

def read_all_constraints() -> List[Tuple[str, str]]:
    """
    Reads all the constraints from the pairings/ folder.
    Returns:
        constraints: List[Tuple[str, str]], a list of IDs pairs to avoid pairing.
    """
    constraints = []

    # all previous pairings and constraints are stored in pairings/*.csv
    csv_filenames = os.listdir(os.path.join(os.getcwd(), PAIRINGS_LOCATION))
    for csv_filename in csv_filenames:
        if os.path.splitext(csv_filename)[1] != ".csv":
            print(f"Skipping {csv_filename} because it is not a csv file.")
            continue
        with open(os.path.join(PAIRINGS_LOCATION, csv_filename)) as csv_file:
            for row in csv.reader(csv_file):
                constraints.append(row)
    
    # translate names to IDs
    return constraints
        
def write_schedule(pairings: List[Tuple[str, str]]):
    """
    Writes the pairings to a new csv file in the pairings/temp folder.
    Inputs:
        pairings: List[Tuple[str, str]], a list of IDs pairs to avoid pairing.
    """
    pass

def generate_ids(names: List[str]) -> Dict[str, int]:
    # read ids from csv
    names_to_ids = {}
    csv_filename = os.path.join(IDS_LOCATION, "ids.csv")
    if os.path.exists(csv_filename):
        with open(csv_filename) as csv_file:
            for name, num_id in csv.reader(csv_file):
                names_to_ids[name] = int(num_id)
    
    # generate new ids
    for name in names:
        if name not in names_to_ids:
            print(f"New participant: {name}. adding ID")
            names_to_ids[name] = len(names_to_ids)
    
    # write ids to csv
    with open(csv_filename, "w") as csv_file:
        for name, num_id in names_to_ids.items():
            csv_file.write(f"{name},{num_id}\n")
    
    return names_to_ids
