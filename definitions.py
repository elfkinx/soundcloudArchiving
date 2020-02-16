import os
import logging
from pathlib import Path

"""
scdownload (SoundCloud Downloader)

This file defines the common constants to be used in different parts of the program

"""

# Default logging format
logging.basicConfig(level=logging.INFO,format="scdownload - INFO: %(message)s")

# The project Root directory
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# The root directory for storing downloaded track data
DATA_PATH = os.path.join(ROOT_DIR, 'data')

logging.info("Ensuring data dir created: " + DATA_PATH)
# We create the root data directory if it doesn't already exist (including any parent directories that don't exist)
Path(DATA_PATH).mkdir(parents=True, exist_ok=True) # ensure data dir exists
