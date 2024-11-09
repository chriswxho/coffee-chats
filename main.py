import argparse
import os
import itertools
from csv_utils import read_all_constraints, generate_ids, read_participants, write_schedule
from matching import matchmake


PAIRINGS_LOCATION = "pairings"
IDS_LOCATION = "ids"

def main(participants_filename: str, results_filename: str):
    # 1. load participants and constraints
    participant_names = read_participants(participants_filename)
    constraints_names = read_all_constraints(os.path.join(os.getcwd(), PAIRINGS_LOCATION))
    
    # 2. load existing IDs for repeat names and generate IDs for names
    unique_constraint_names = set(itertools.chain(*constraints_names))
    all_names = unique_constraint_names | set(participant_names)
    names_to_ids = generate_ids(all_names, IDS_LOCATION)
    ids_to_names = {v: k for k, v in names_to_ids.items()}

    # 3. preprocess participants and constraints
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
        res_ids = matchmake(participant_ids, constraints_ids)

        # 4. write matches to file
        matches_filename = os.path.join(os.getcwd(), PAIRINGS_LOCATION, results_filename)
        res = []
        for pair_id in res_ids:
            res.append([ids_to_names[pair_id[0]], ids_to_names[pair_id[1]]])
        write_schedule(res, matches_filename)

        # 5. confirm with user
        choice = None
        while choice != "Y" and choice != "y" and choice != "N":
            choice = input(f"Check over the file {matches_filename}. Y/y to finish, N to restart.")
        if choice == "N":
            print(f"Deleting generated matches file at {matches_filename}, restart matchmaking.")
            os.remove(matches_filename)
            matches_filename = None
        else:
            print(f"Finished matchmaking, results saved to {matches_filename}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the coffee matching app!")
    parser.add_argument('participants_filename', help="CSV file containing the participants' names for this week.")
    parser.add_argument('results_filename', help="CSV file (filename only) to write the results to.")
    parser.add_argument('-v', '--verbose',
                        action='store_true')  # on/off flag
    args = parser.parse_args()

    main(args.participants_filename)
