import sys
import logging
import argparse
import os
import itertools
from csv_utils import read_all_constraints, generate_ids, read_participants, write_schedule
from matching import matchmake


PAIRINGS_LOCATION = "pairings"
IDS_LOCATION = "ids"


logger = logging.getLogger(__name__)

def init_logging(logger, verbose: bool):
    log_handler = logging.StreamHandler()
    log_handler.setStream(sys.stderr)
    log_handler.setFormatter(
        logging.Formatter("[%(asctime)s.%(msecs)03d %(filename)s:%(lineno)s] %(levelname)s: %(message)s")
    )

    root_logger = logging.getLogger()
    root_logger.addHandler(log_handler)
    if verbose:
        root_logger.setLevel(logging.DEBUG)
        root_logger.debug("Verbose logging enabled")
    else:
        root_logger.setLevel(logging.INFO)

def main(participants_filename: str, results_filename: str):
    # 1. load participants and constraints
    constraints_filename = os.path.join(os.getcwd(), PAIRINGS_LOCATION)
    logger.info(f"Loading participants from {participants_filename}, and constraints from {constraints_filename}")
    participant_names = read_participants(participants_filename)
    constraints_names = read_all_constraints(constraints_filename)
    
    # 2. load existing IDs for repeat names and generate IDs for names
    logger.info("Generating IDs for participants and constraints")
    unique_constraint_names = set(itertools.chain(*constraints_names))
    all_names = unique_constraint_names | set(participant_names)
    names_to_ids = generate_ids(all_names, IDS_LOCATION)
    ids_to_names = {v: k for k, v in names_to_ids.items()}

    # 3. preprocess participants and constraints
    logger.info("Preprocessing participants and constraints")
    constraints_ids = []
    for constraint_name in constraints_names:
        constraints_ids.append(
            [
                names_to_ids[constraint_name[0]],
                names_to_ids[constraint_name[1]],
            ]
        )
    participant_ids = [names_to_ids[name] for name in participant_names]

    matches_filename = None
    while matches_filename is None:
        # 3. matchmaking!
        logger.info("Running matchmaking")
        res_ids = matchmake(participant_ids, constraints_ids)

        # 4. write matches to file
        matches_filename = os.path.join(os.getcwd(), PAIRINGS_LOCATION, results_filename)
        res = []
        for pair_id in res_ids:
            res.append([ids_to_names[pair_id[0]], ids_to_names[pair_id[1]]])
        write_schedule(res, matches_filename)

        # 5. confirm with user
        choice = None
        while choice not in {"Y", "y", "N", "Q"}:
            choice = input(f"Check over the file {matches_filename}. Y/y to finish, N to restart, Q to exit.\n")
        if choice == "N":
            logger.info(f"Deleting generated matches file at {matches_filename}, restart matchmaking.")
            os.remove(matches_filename)
            matches_filename = None
        elif choice == "Q":
            logger.info(f"Deleting generated matches file at {matches_filename}, exiting.")
            os.remove(matches_filename)
        else:
            logger.info(f"Finished matchmaking, results saved to {matches_filename}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the coffee matching app!")
    parser.add_argument('participants_filename', help="CSV file containing the participants' names for this week.")
    parser.add_argument(
        'results_filename', 
        help="CSV file (filename only) to write the results to. Automatically saves to pairings/ folder."
    )
    parser.add_argument('-v', '--verbose',
                        action='store_true')  # on/off flag
    args = parser.parse_args()

    

    # logging
    init_logging(logger, args.verbose)

    main(args.participants_filename, args.results_filename)
