import itertools
from csv_utils import read_all_constraints, generate_ids

if __name__ == "__main__":
    constraints = read_all_constraints()
    unique_names = list(itertools.chain(*constraints))
    ids = generate_ids(unique_names)
