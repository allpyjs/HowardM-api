# watchdog_cli.py

import json
import time
import logging
import logging.config
import argparse
from watchdog.observers import Observer

from hm_api.watchdog.events import WorkerFileSystemEventHandler
from hm_api.logger import LOGGING
from hm_api import config

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logging.config.dictConfig(LOGGING)

    logger.info("Starting watchdog version %s", config.PROJECT_VERSION)

    parser = argparse.ArgumentParser(description='hm watchdog worker')

    parser.add_argument('-c', nargs=1, help='JSON configuration file')
    
    args = parser.parse_args()

    config_file = args.c[0] if args.c is not None and len(
        args.c) > 0 else 'watchdog.json'

    with open(config_file) as json_config:
        cfg = json.load(json_config)

    event_handler = WorkerFileSystemEventHandler(cfg)
    observer = Observer()
    observer.schedule(event_handler, cfg['base_path'], recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    finally:
        observer.stop()
        observer.join()
