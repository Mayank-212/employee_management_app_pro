# main.py

from gui import run_gui
from config_handler import load_config
from utils.helpers import initialize_app_environment


if __name__ == "__main__":
    # Step 1: Prepare folders, database files, logs etc.
    initialize_app_environment()

    # Step 2: Check if current time >= auto-start time and auto-start is enabled
    config = load_config()


    # Step 3: Show GUI Dashboard


    run_gui()
