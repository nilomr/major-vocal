import contextlib
import json
import multiprocessing
from datetime import datetime
from multiprocessing import Manager
from pathlib import Path

import polars as pl
from birdnetlib import Recording
from birdnetlib.analyzer import Analyzer
from tqdm import tqdm

from majorvocal.config import config

# Read in the metadata (see https://nilomr.github.io/great-tit-hits/)
data_path = config.PROJECT_STRUCTURE["metadata"] / "main.csv"
data = pl.read_csv(data_path)

# Ged directories matching entries with recordings
pnum = data.filter(data["n_vocalisations"] > 0)["pnum"]
folders = list(Path(config.DATA_PATH).glob("*/*/"))
pnum_folders = [folder for folder in folders if folder.name in pnum]

# Get list of all .WAV in pnum_folders and keep files between 033000 and 063000
file_paths = [f for folder in pnum_folders for f in folder.glob("*.WAV")]
file_paths = [f for f in file_paths if "033000" < f.stem.split("_")[1] < "063000"][:8]

# Create output dir for json files
json_dir = config.PROJECT_STRUCTURE["derived_data"] / "json"
json_dir.mkdir(parents=True, exist_ok=True)


def process_file(file_path: Path):
    """
    Runs BirdNET analyzer on a single file. It saves the analyzed detections to
    a JSON file and logs the process to a log file.

    Args:
        file_path (str): The path to the file to be processed.

    Returns:
        None
    """
    date = datetime.strptime(file_path.stem.split("_")[0], "%Y%m%d")
    dir_name = file_path.parent.name

    recording = Recording(
        analyzer,
        str(file_path),
        lat=51.775036,
        lon=-1.336488,
        date=date,
        min_conf=0.8,
    )
    log_date = datetime.now().strftime("%Y-%m-%d %H:%M")
    log_file = Path(config.PROJECT_PATH, "logs", f"{log_date}.log")
    log_file.parent.mkdir(parents=True, exist_ok=True)
    with open(log_file, "a") as f:
        with contextlib.redirect_stdout(f):
            recording.analyze()

    # Save recording.detections to a json file
    with open(Path(json_dir, f"{file_path.stem}.json"), "w") as f:
        json.dump(recording.detections, f)

    detections_queue.put([file_path.stem, dir_name, recording.detections])


# ──── INFERENCE ──────────────────────────────────────────────────────────────

# Load and initialize the BirdNET-Analyzer model
analyzer = Analyzer(version="2.4")

# Create a shared queue to store the detections
manager = Manager()
detections_queue = manager.Queue()

# Create a pool of worker processes
pool = multiprocessing.Pool(processes=4)
start = datetime.now()

# Map to the pool
detections = []
with tqdm(total=len(file_paths), desc="Processing files") as pbar:
    for _ in pool.imap_unordered(process_file, file_paths):
        pbar.update(1)
        while not detections_queue.empty():
            detections.append(detections_queue.get())

# Close the pool and wait for all processes to finish
pool.close()
pool.join()

# Save the reults to a json file
detections_file = Path(config.PROJECT_PATH, "data", "derived")
detections_file.mkdir(parents=True, exist_ok=True)
detections_file = Path(detections_file, "detections.json")
with open(detections_file, "w") as f:
    json.dump(detections, f)


end = datetime.now()
print(f"Time taken: {end - start}")
