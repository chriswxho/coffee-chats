import argparse
import itertools
from csv_utils import read_all_constraints, generate_ids, read_participants
from matching import matchmake

def main(participants_filename: str):
    constraints = read_all_constraints()
    unique_names = list(itertools.chain(*constraints))
    names_to_ids = generate_ids(unique_names)
    ids_to_names = {v: k for k, v in names_to_ids.items()}

    # 1: preprocess constraints
    constraints_ids = []
    for constraint in constraints:
        constraints_ids.append(
            [
                names_to_ids[constraint[0]],
                names_to_ids[constraint[1]],
            ]
        )

    # 2. preprocess participants
    participant_names = read_participants(participants_filename)
    participant_ids = [names_to_ids[name] for name in participant_names]

    # 3. matchmaking!
    res_ids = matchmake(participant_ids, constraints_ids)

    # 4. confirm with user
    res = []
    for pair_id in res_ids:
        res.append([ids_to_names[pair_id[0]], ids_to_names[pair_id[1]]])
    print(res)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('participants_filename')
    parser.add_argument('-v', '--verbose',
                        action='store_true')  # on/off flag
    args = parser.parse_args()

    main(args.participants_filename)
