import os
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO,format="scdownload - INFO: %(message)s")

ROOT_DIR = os.path.dirname(os.path.abspath(__file__)) # This is your Project Root
DATA_PATH = os.path.join(ROOT_DIR, 'data')  # requires `import os`

logging.debug("Ensuring data dir created: " + DATA_PATH)
Path(DATA_PATH).mkdir(parents=True, exist_ok=True) # ensure data dir exists
