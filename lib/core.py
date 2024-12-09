import sys
import logging
import os
import itertools
from csv_utils import read_all_pairings, generate_ids, read_participants, write_pairings
from matching import matchmake, get_all_pairing_history
import datetime
from typing import Dict, List, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)

PAIRINGS_LOCATION = "pairings"
IDS_LOCATION = "ids"
LOGS_LOCATION = "logs"

log_file = os.path.join(LOGS_LOCATION, f"coffee-chat-debug-logs-{datetime.datetime.now()}.txt")


def init_logging(verbose=False) -> None:
    root_logger = logging.getLogger()
        
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        if not os.path.exists(LOGS_LOCATION):
            os.mkdir(LOGS_LOCATION)
        log_handler = logging.FileHandler(log_file)
    else:
        log_handler = logging.StreamHandler(sys.stderr)

    log_handler.setFormatter(
        logging.Formatter(
            "[%(asctime)0s.%(msecs)03d %(filename)s:%(lineno)s] %(levelname)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )

    root_logger.addHandler(log_handler)
    if verbose:
        root_logger.setLevel(logging.DEBUG)
        root_logger.debug("Verbose logging enabled")
    else:
        root_logger.setLevel(logging.INFO)


@dataclass
class CoffeeChatLoadData:
    participant_names: List[str]
    constraints_names: List[Tuple[str, str]]


class CoffeeChatCore:
    def __init__(self, participants_filename: str, results_filename: str):
        # both of these now refer to absolute paths
        self.participants_filename = participants_filename
        self.results_filename = os.path.join(PAIRINGS_LOCATION, results_filename)
        self.names_to_ids: Dict[str, int] = {}
        self.verbose = False

    def load_data(
        self,
        constraints_filename: str = os.path.join(PAIRINGS_LOCATION, "CONSTRAINTS.csv"),
        ids_filename: str = os.path.join(IDS_LOCATION, "ids.csv"),
    ) -> CoffeeChatLoadData:
        logger.info(f"Loading participants from {self.participants_filename}")
        participant_names = read_participants(self.participants_filename)

        constraints_dirname = os.path.join(os.getcwd(), PAIRINGS_LOCATION)
        logger.info(f"Loading constraints from directory {constraints_dirname}")
        constraints_names = []
        for filename in os.listdir(constraints_dirname):
            constraints_filename = os.path.join(constraints_dirname, filename)
            constraints_names.extend(read_all_pairings(constraints_filename))

        logger.info("Generating IDs for participants and constraints")
        unique_constraint_names = set(itertools.chain(*constraints_names))
        participants = set(participant_names)
        all_names = unique_constraint_names | participants
        self.names_to_ids = generate_ids(list(all_names), ids_filename)

        return CoffeeChatLoadData(participant_names, constraints_names)

    def run_matchmaking(
        self,
        participant_names: List[str],
        constraints_names: List[Tuple[str, str]],
    ) -> List[Tuple[str, str]]:
        logger.info("Running matchmaking")
        preprocess_data = self._preprocess_participants(
            participant_names, constraints_names
        )
        participant_ids = preprocess_data[0]
        constraints_ids = preprocess_data[1]

        pair_ids = matchmake(participant_ids, constraints_ids)
        res_pair_names = self._postprocess_matches(pair_ids)

        return res_pair_names

    def sanity_check_matches(
        self,
        pair_names: List[Tuple[str, str]],
        participant_names: List[str],
        pairings_dirname: str = PAIRINGS_LOCATION,
    ) -> bool:
        # sanity check that everyone is paired, and that pairs were never repeated
        logger.info("Checking that everyone that is participating has been paired...")
        actual_participants = set(itertools.chain(*pair_names))
        nonparticipants = set(participant_names) - actual_participants
        if len(nonparticipants) == 0:
            logger.info("All participants were paired successfully!")
        else:
            logger.error("Some people left unpaired :(")
            logger.error(f"Unpaired folks: {nonparticipants}")
            return False

        logger.info("Checking that no pairings are repeats...")
        history = {}
        # grab all the previous pairing history
        csv_filenames = os.listdir(pairings_dirname)
        for filename in csv_filenames:
            if filename.endswith("constraints.csv"):
                logger.debug('Skipping "constraints.csv" file during history check')
                continue
            csv_filename = os.path.join(pairings_dirname, filename)
            history[csv_filename] = read_all_pairings(csv_filename)
        # also add in currently generated pairings
        history[self.results_filename] = pair_names

        all_histories = get_all_pairing_history(history)
        if all(len(history) == 1 for history in all_histories.values()):
            logger.info("All pairings are new and haven't been repeated!")
        else:
            logger.error(
                "Some invalid pairings. Repeated pairings, and offending files:"
            )
            for pair_name, filenames in all_histories.items():
                if len(filenames) > 1:
                    logger.error(f"{pair_name[0]} & {pair_name[1]}: {filenames}")
            return False
        return True

    def finalize_matches(self, pair_names: List[Tuple[str, str]]) -> None:
        write_pairings(pair_names, self.results_filename)

    def _preprocess_participants(
        self,
        participant_names: List[str],
        constraints_names: List[Tuple[str, str]],
    ) -> Tuple[List[int], List[Tuple[int, int]]]:
        constraints_ids = []
        for constraint_name in constraints_names:
            constraints_ids.append(
                [
                    self.names_to_ids[constraint_name[0]],
                    self.names_to_ids[constraint_name[1]],
                ]
            )
        participant_ids = [self.names_to_ids[name] for name in participant_names]
        return (participant_ids, constraints_ids)

    def _postprocess_matches(
        self,
        pair_ids: List[Tuple[int, int]],
    ) -> List[Tuple[str, str]]:
        ids_to_names = {v: k for k, v in self.names_to_ids.items()}
        res_pair_names = [
            (ids_to_names[pair_id[0]], ids_to_names[pair_id[1]]) for pair_id in pair_ids
        ]

        return res_pair_names
