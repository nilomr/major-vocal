import subprocess
from pathlib import Path

from majorvocal.config import config

# Wytham Great Tit song metadata - download and unzip
folder_url = "https://files.de-1.osf.io/v1/resources/n8ac9/providers/osfstorage/64898c4bc861160288251fd1/?zip"
save_path = config.PROJECT_STRUCTURE["metadata"] / "metadata.zip"

subprocess.run(["wget", "--show-progress", "--progress=bar:force 2>&1", "-O", str(save_path), folder_url])
subprocess.run(["unzip", str(save_path), "-d", str(save_path.parent)])

# Download first song times (manual annotations)
times_url = "https://raw.githubusercontent.com/nilomr/great-tit-hits-setup/main/resources/birds/times.csv"
save_times_path = config.PROJECT_STRUCTURE["metadata"] / "times.csv"

subprocess.run(["wget", "--show-progress", "--progress=bar:force 2>&1", "-O", str(save_times_path), times_url])
