import logging
import argparse
import os

from core import init_logging, CoffeeChatCore


logger = logging.getLogger(__name__)


def main(participants_filename: str, results_filename: str):
    core = CoffeeChatCore(
        participants_filename=participants_filename,
        results_filename=results_filename,
    )
    loaded_data = core.load_data()

    participant_names = loaded_data.participant_names
    constraints_names = loaded_data.constraints_names

    if len(participant_names) % 2 == 1:
        skip_choice = None
        logger.error("Odd number of participants this month! Who are we leaving out?")
        while skip_choice not in list("EeMmQ"):
            skip_choice = input(
                "Press (E/e) for Eliette, (M/m) for Michael, Q to exit.\n"
            )

        if skip_choice in "Ee":
            participant_names.remove("Eliette Seo")
        elif skip_choice in "Mm":
            participant_names.remove("Michael Youn")
        else:  # skip_choice was Q
            logger.info("Quitting after not being able to agree on who to skip :(")
            exit(0)

    while not os.path.exists(core.results_filename):
        pair_names = core.run_matchmaking(
            participant_names=participant_names,
            constraints_names=constraints_names,
        )
        core.sanity_check_matches(
            pair_names,
            participant_names,
        )
        core.finalize_matches(pair_names)

        choice = None
        while choice not in list("YyNnQ"):
            choice = input(
                f"Check over the file {core.results_filename}. (Y/y) to finish, (N/n) to restart, Q to exit.\n"
            )
        if choice in "Nn":
            logger.info(
                f"Deleting generated matches file at {core.results_filename}, restart matchmaking."
            )
            os.remove(core.results_filename)
        elif choice == "Q":
            logger.info(
                f"Deleting generated matches file at {core.results_filename}, exiting."
            )
            os.remove(core.results_filename)
            break
        else:  # choice is Y or y
            logger.info(
                f"Finished matchmaking, results saved to {core.results_filename}"
            )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the coffee matching app!")
    parser.add_argument(
        "participants_filename",
        help="CSV file containing the participants' names for this week.",
    )
    parser.add_argument(
        "results_filename",
        help="CSV file (filename only) to write the results to. Automatically saves to pairings/ folder.",
    )
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    init_logging(args.verbose)
    main(args.participants_filename, args.results_filename)
