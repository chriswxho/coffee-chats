import sys
import logging
import argparse
import os
import itertools
from csv_utils import read_all_pairings, generate_ids, read_participants, write_pairings
from matching import matchmake, get_all_pairing_history
import csv


PAIRINGS_LOCATION = "pairings"
IDS_LOCATION = "ids"


logger = logging.getLogger(__name__)

def init_logging(verbose: bool):
    log_handler = logging.StreamHandler()
    log_handler.setStream(sys.stderr)
    log_handler.setFormatter(
        logging.Formatter(
            "[%(asctime)0s.%(msecs)03d %(filename)s:%(lineno)s] %(levelname)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
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

    # 1.5) if there's an odd number of participants, take out either E or M!
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
    participants = set(participant_names)
    all_names = unique_constraint_names | participants
    names_to_ids = generate_ids(list(all_names), IDS_LOCATION)
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
        # 4) matchmaking algorithm
        logger.info("Running matchmaking")
        pair_ids = matchmake(participant_ids, constraints_ids)
        res_pair_names = [(ids_to_names[pair_id[0]], ids_to_names[pair_id[1]]) for pair_id in pair_ids]

        # 5) sanity check that everyone is paired, and that pairs were never repeated
        logger.info("Checking that everyone that is participating has been paired...")
        actual_participants = set(itertools.chain(*res_pair_names))
        nonparticipants = participants - actual_participants
        if len(nonparticipants) == 0:
            logger.info("All participants were paired successfully!")
        else:
            logger.error("Some people left unpaired :(")
            logger.error(f"Unpaired folks: {nonparticipants}")
        
        logger.info("Checking that no pairings are repeats...")
        history = {}
        # grab all the previous pairing history
        csv_filenames = os.listdir(constraints_dirname)
        for filename in csv_filenames:
            if filename.endswith("constraints.csv"):
                logger.debug("Skipping \"constraints.csv\" file during history check")
                continue
            csv_filename = os.path.join(constraints_dirname, filename)
            history[csv_filename] = read_all_pairings(csv_filename)
        # also add in currently generated pairings
        history[results_filename] = res_pair_names
        
        all_histories = get_all_pairing_history(history)
        if all(len(history) == 1 for history in all_histories.values()):
            logger.info("All pairings are new and haven\'t been repeated!")
        else:
            logger.error("Some invalid pairings. Repeated pairings, and offending files:")
            for pair_names, filenames in all_histories.items():
                if len(filenames) > 1:
                    logger.error(f"{pair_names[0]} & {pair_names[1]}: {filenames}")

        # 6) write matches to file
        matches_filename = os.path.join(os.getcwd(), PAIRINGS_LOCATION, results_filename)
        write_pairings(res_pair_names, matches_filename)
        
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

    init_logging(args.verbose)

    main(args.participants_filename, args.results_filename)
