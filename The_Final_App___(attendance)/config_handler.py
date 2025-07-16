# utils/config_handler.py

import json
import os

CONFIG_FILE = "config.json"

# Default values
default_config = {
    "admin_password": "6965",
    "auto_start_time": "09:00",
    "auto_start_enabled": False,
    "fingerprint_port": "COM3",
    "entry_cutoff_time": "10:00",
    "exit_cutoff_time": "17:00",
    "data_directory": "data"
}

def load_config():
    if not os.path.exists(CONFIG_FILE):
        save_config(default_config)
    try:
        with open(CONFIG_FILE, "r") as file:
            return json.load(file)
    except json.JSONDecodeError:
        return default_config

def save_config(data):
    config = load_config()
    config.update(data)
    with open(CONFIG_FILE, "w") as file:
        json.dump(config, file, indent=4)


