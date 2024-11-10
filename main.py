import sys
import logging
import argparse
import os
import itertools
from csv_utils import read_all_pairings, generate_ids, read_participants, write_pairings
from matching import matchmake, check_pairing_history
import csv


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
    # 1) load participants and constraints
    constraints_dirname = os.path.join(os.getcwd(), PAIRINGS_LOCATION)
    logger.info(f"Loading participants from {participants_filename}, and constraints from directory {constraints_dirname}")
    participant_names = read_participants(participants_filename)
    constraints_names = []
    for filename in os.listdir(constraints_dirname):
        constraints_filename = os.path.join(constraints_dirname, filename)
        constraints_names.extend(read_all_pairings(constraints_filename))

    # 1.5) if there's an odd number of participants, swap between E and M!
    if len(participant_names) % 2 == 1:
        skip_choice = None
        logger.error("Odd number of participants this month! Who are we leaving out?")
        while skip_choice not in list("EeMmQ"):
            skip_choice = input("Press (E/e) for Eliette, (M/m) for Michael, Q to exit.\n")
        
        if skip_choice in "Ee":
            participant_names.remove("Eliette Seo")
        elif skip_choice in "Mm":
            participant_names.remove("Michael Youn")
        else: # skip_choice was Q
            logger.info("Quitting after not being able to agree on who to skip :(")
            exit(0)
        
    # 2) load existing IDs for repeat names and generate IDs for names
    logger.info("Generating IDs for participants and constraints")
    unique_constraint_names = set(itertools.chain(*constraints_names))
    all_names = unique_constraint_names | set(participant_names)
    names_to_ids = generate_ids(all_names, IDS_LOCATION)
    ids_to_names = {v: k for k, v in names_to_ids.items()}

    # 3) preprocess participants and constraints
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
        # 4) matchmaking algorithm via blossom + primal dual method
        logger.info("Running matchmaking")
        res_ids = matchmake(participant_ids, constraints_ids)

        # 5) write matches to file
        matches_filename = os.path.join(os.getcwd(), PAIRINGS_LOCATION, results_filename)
        res = []
        for pair_id in res_ids:
            res.append([ids_to_names[pair_id[0]], ids_to_names[pair_id[1]]])
        write_pairings(res, matches_filename)

        # 6) sanity check that everyone is paired, and that pairs were never repeated
        actual_participant_ids = set(itertools.chain(*res_ids))
        nonparticipant_ids = set(participant_ids) - actual_participant_ids
        if len(nonparticipant_ids) == 0:
            logger.info("All participants were paired successfully!")
        else:
            logger.error("Some people left unpaired :(")
            logger.error(f"Unpaired folks: {[ids_to_names[idx] for idx in nonparticipant_ids]}")

        csv_filenames = os.listdir(constraints_dirname)
        history = {}
        for csv_filename in csv_filenames:
            pairings = read_all_pairings(csv_filename)
            history[csv_filename] = pairings
        
        all_histories = check_pairing_history(history)
        if all(len(history) == 1 for history in all_histories.values()):
            logger.info("All pairings are valid!")
        else:
            logger.error("Some invalid pairings. Repeated pairings, and offending files:")
            for pairing, filenames in all_histories.items():
                logger.error(f"{ids_to_names[pairing[0]] - ids_to_names[pairing[1]]}: {filenames}")
        
        # 7) confirm with user
        choice = None
        while choice not in list("YyNnQ"):
            choice = input(f"Check over the file {matches_filename}. (Y/y) to finish, (N/n) to restart, Q to exit.\n")
        if choice in "Nn":
            logger.info(f"Deleting generated matches file at {matches_filename}, restart matchmaking.")
            os.remove(matches_filename)
            matches_filename = None
        elif choice == "Q":
            logger.info(f"Deleting generated matches file at {matches_filename}, exiting.")
            os.remove(matches_filename)
        else: # choice is Y or y
            logger.info(f"Finished matchmaking, results saved to {matches_filename}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the coffee matching app!")
    parser.add_argument('participants_filename', help="CSV file containing the participants' names for this week.")
    parser.add_argument(
        'results_filename', 
        help="CSV file (filename only) to write the results to. Automatically saves to pairings/ folder."
    )
    parser.add_argument('-v', '--verbose', action='store_true')
    args = parser.parse_args()

    

    # logging
    init_logging(logger, args.verbose)

    main(args.participants_filename, args.results_filename)
