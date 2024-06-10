import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.spatial import distance
from sklearn.manifold import MDS

from majorvocal.config import config

detections_file = Path(config.PROJECT_PATH, "data", "derived", "detections.json")


# ──── PLOT SETTINGS ──────────────────────────────────────────────────────────

plt.rcParams.update(
    {
        "axes.facecolor": "#1d1d1d",
        "figure.facecolor": "#1d1d1d",
        "text.color": "white",
        "axes.labelcolor": "white",
        "xtick.color": "white",
        "ytick.color": "white",
        "axes.edgecolor": "white",
        "axes.titlecolor": "white",
        "axes.titlepad": 17,
        "font.size": 15,  # set all text size to 15
        "xtick.labelsize": 13,  # set x-axis tick font size to 13
        "ytick.labelsize": 13,  # set y-axis tick font size to 13
    }
)
site_palette = [plt.get_cmap("Spectral", 7)(i) for i in range(7)]
cluster_palette = ["#ed6a5a", "#f4f1bb", "#9bc1bc"]
cluster_palette_4 = ["#335c67", "#fff3b0", "#e09f3e", "#9e2a2b"]

figwidth = 8
textsize = 15

# ──── DATA INGEST ────────────────────────────────────────────────────────────

# Read the detections from the json file and convert to a pandas DataFrame
with open(detections_file, encoding="utf-8") as file:
    detections = json.load(file)

df = pd.DataFrame(detections, columns=["file_name", "site", "detections"])
df = df.explode("detections").dropna(subset=["detections"])
df = pd.concat([df, df["detections"].apply(pd.Series)], axis=1)
df["start_time"] = pd.to_datetime(df["file_name"], format="%Y%m%d_%H%M%S") + pd.to_timedelta(df["start_time"], unit="s")
df["end_time"] = pd.to_datetime(df["file_name"], format="%Y%m%d_%H%M%S") + pd.to_timedelta(df["end_time"], unit="s")
df = df.sort_values(["file_name", "start_time"])
df["time_bin"] = df["start_time"].dt.floor("30min")


# Plot a histogram of 'start_time' to check the distribution of detections over
# time
# extract the time only from the start_time column
df["start_time_time"] = df["start_time"].dt.strftime("%H:%M")

# Convert start_time_time to numeric values
df["start_time_numeric"] = df["start_time_time"].apply(lambda x: int(x.split(":")[0]) * 60 + int(x.split(":")[1]))
plt.figure(figsize=(figwidth, 4))
plt.hist(df["start_time_numeric"], bins=20, color=site_palette[0], edgecolor="white")
plt.xlabel("Time (HHMM)")
plt.ylabel("Number of detections")
plt.title("Distribution of detections over time")
plt.xticks(rotation=45)
# Format x-axis labels as HHMM
plt.gca().xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: "{:02d}{:02d}".format(int(x) // 60, int(x) % 60)))
plt.tight_layout()
plt.show()
