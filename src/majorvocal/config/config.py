from pathlib import Path

# Paths
DATA_PATH = Path("/media/nilomr/SONGDATA/wytham-great-tit/raw/")
PROJECT_PATH = Path(__file__).resolve().parents[3]

# Project structure
PROJECT_STRUCTURE = {
    "metadata": PROJECT_PATH / "data" / "metadata",
    "figures": PROJECT_PATH / "output" / "figures",
    "derived_data": PROJECT_PATH / "data" / "derived",
}

# Create the project structure folders if they don't exist already:
for folder in PROJECT_STRUCTURE.values():
    folder.mkdir(parents=True, exist_ok=True)
