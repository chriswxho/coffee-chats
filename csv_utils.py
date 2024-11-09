import logging
import os
import csv
import datetime
from typing import Dict, List, Tuple


logger = logging.getLogger(__name__)

def read_all_constraints(constraints_dir: str) -> List[Tuple[str, str]]:
    """
    Reads all the constraints from the pairings/ folder.
    Returns:
        constraints: List[Tuple[str, str]], a list of IDs pairs to avoid pairing.
    """
    constraints = []

    # all previous pairings and constraints are stored in pairings/*.csv
    csv_filenames = os.listdir(constraints_dir)
    for csv_filename in csv_filenames:
        if os.path.splitext(csv_filename)[1] != ".csv":
            logger.info(f"Skipping \"{csv_filename}\" because it is not a csv file.")
            continue
        with open(os.path.join(constraints_dir, csv_filename)) as csv_file:
            for row in csv.reader(csv_file):
                constraints.append(row)
    
    # translate names to IDs
    return constraints

def read_participants(participants_file: str) -> List[str]:
    """
    Reads all the participants from the pairings/ folder.
    Returns:
        participants: List[str], a list of participant names.
    """
    participants = []

    # this week's participants should be part of cli input
    if os.path.splitext(participants_file)[1] != ".csv":
        raise RuntimeError(f"participants_file {participants_file} is not a csv file.")
    
    with open(participants_file) as csv_file:
        for name in csv.reader(csv_file):
            participants.append(name[0])
    
    return participants
        
def write_schedule(pairings: List[Tuple[str, str]], destination: str) -> str:
    """
    Writes the pairings to a new csv file in the pairings/temp folder.
    Inputs:
        pairings: List[Tuple[str, str]], a list of IDs pairs to avoid pairing.
    Outputs:
        filename: str, the name of the csv file that was written.
    """
    with open(destination, "w") as f:
        for pair in pairings:
            csv.writer(f).writerow(pair)

def generate_ids(names: List[str], ids_dir: str) -> Dict[str, int]:
    # read ids from csv
    names_to_ids = {}
    csv_filename = os.path.join(ids_dir, "ids.csv")
    if os.path.exists(csv_filename):
        with open(csv_filename) as csv_file:
            for name, num_id in csv.reader(csv_file):
                names_to_ids[name] = int(num_id)
    
    # generate new ids
    for name in names:
        if name not in names_to_ids:
            logger.debug(f"New participant, adding name-ID pair {name}: {len(names_to_ids)}")
            names_to_ids[name] = len(names_to_ids)
    
    # write new ids to csv
    with open(csv_filename, "w") as csv_file:
        writer = csv.writer(csv_file)
        for name, num_id in names_to_ids.items():
            writer.writerow([name, num_id])
    
    return names_to_ids
