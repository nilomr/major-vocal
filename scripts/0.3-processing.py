import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from majorvocal.config import config
from majorvocal.graphical import figwidth, site_palette
from majorvocal.utils import extract_parus_major, to_df

detections_file = Path(config.PROJECT_PATH, "data", "derived", "detections.json")
brood_file = Path(config.PROJECT_PATH, "data", "metadata", "main.csv")
coords_file = Path(config.PROJECT_PATH, "data", "metadata", "nestboxes.csv")

# ──── DATA INGEST ────────────────────────────────────────────────────────────


# Function to read JSON file and convert to DataFrame
def read_json_to_df(filepath, extract_func):
    with open(filepath, encoding="utf-8") as file:
        return to_df(extract_func(json.load(file)))


# Function to preprocess detections
def preprocess_detections(detections, brood_data):
    detections["count"] = detections["confidence"].notna().astype(int)
    daily_counts = detections.groupby(["pnum", "date"], as_index=False)["count"].sum()
    daily_counts = daily_counts.merge(brood_data, on="pnum")
    daily_counts["date"] = pd.to_datetime(daily_counts["date"])
    daily_counts["lay_date"] = pd.to_datetime(daily_counts["lay_date"])
    daily_counts["days_from_lay"] = (daily_counts["date"] - daily_counts["lay_date"]).dt.days
    return daily_counts


# Function to ensure all dates within range are present
def ensure_date_range(daily_counts):
    date_range = (
        daily_counts.groupby("pnum")["date"]
        .agg(["min", "max"])
        .rename(columns={"min": "date_first", "max": "date_last"})
    )
    daily_counts = daily_counts.merge(date_range, on="pnum")
    return daily_counts[
        (daily_counts["date"] >= daily_counts["date_first"]) & (daily_counts["date"] <= daily_counts["date_last"])
    ]


# Read and process data
pmajor = read_json_to_df(detections_file, extract_parus_major)
brood_data = pd.read_csv(brood_file)
coords = pd.read_csv(coords_file)
daily_counts = preprocess_detections(pmajor, brood_data)
daily_counts = ensure_date_range(daily_counts)


# Save the processed data to csv files
daily_counts.to_csv(Path(config.PROJECT_PATH, "data", "derived", "daily_counts.csv"), index=False)
pmajor.to_csv(Path(config.PROJECT_PATH, "data", "derived", "all_detections.csv"), index=False)

# ──── SOME GRAPHICAL SANITY CHECKS ───────────────────────────────────────────


# Plot the distribution of number of rows per pnum
fig, ax = plt.subplots(figsize=(figwidth, figwidth / 2))
sns.histplot(data=daily_counts["pnum"].value_counts(), ax=ax)
ax.set_xlabel("Number of Detections")
ax.set_ylabel("Number of Pnums")
plt.tight_layout()


# Plot the distribution of detections per day
fig, ax = plt.subplots(figsize=(10, 4))
grouped_data = pmajor.groupby(["year", "dayofyear"]).size().unstack("year")
grouped_data.columns = grouped_data.columns.astype(int)

# Plot the smoothed lines (5 day rolling average)
for i, year in enumerate(grouped_data.columns):
    smoothed = grouped_data[year].rolling(window=5, min_periods=1).mean()
    ax.plot(
        smoothed.index, smoothed, color=site_palette[i], linewidth=2, linestyle="dotted", label=f"Song activity {year}"
    )

lay_dates = daily_counts[["pnum", "lay_date", "year"]].drop_duplicates()
lay_dates["lay_date"] = lay_dates["lay_date"].dt.dayofyear
lay_dates = lay_dates.groupby(["lay_date", "year"]).size().reset_index(name="count")

# Plot the number of lay_dates for each day on a second y-axis, by year
ax2 = ax.twinx()
for i, year in enumerate(sorted(lay_dates["year"].unique())):
    data = lay_dates[lay_dates["year"] == year]
    smoothed = data["count"].rolling(window=5, min_periods=1).mean()
    ax2.plot(data["lay_date"], smoothed, color=site_palette[i], linewidth=2, label=f"Eggs {year}")

ax.legend(title="Legend", bbox_to_anchor=(1.2, 1), loc="upper left", prop={"size": 10})
ax.set_xlabel("Day")
ax.set_ylabel("Number of Detections")
ax2.set_ylabel("Number of 1st eggs")
ax.set_title("Great tit Detections")
plt.tight_layout()


# Plot the recorded date range for each breeding attempt
fig, ax = plt.subplots(figsize=(15, len(daily_counts["pnum"].unique()) * 0.4))
pnum_positions = {pnum: i for i, pnum in enumerate(daily_counts["pnum"].unique())}
for pnum, group in daily_counts.groupby("pnum"):
    y = pnum_positions[pnum]
    start_day = group["days_from_lay"].min()
    end_day = group["days_from_lay"].max()
    ax.plot([start_day, end_day], [y, y], marker="o", markersize=10, label=pnum)  # Adjust marker size as needed

ax.set_xlabel("Days from Lay Date")
ax.set_ylabel("Pnum")
ax.set_yticks(list(pnum_positions.values()))
ax.set_yticklabels(list(pnum_positions.keys()))
ax.grid(True)
ax.set_title("Gantt Chart of Pnum Activities Centered Around Lay Date")
ax.legend(title="Pnum", bbox_to_anchor=(1.05, 1), loc="upper left")
plt.tight_layout()
plt.show()


# Calculate how far the peak in song activity is from the lay_date
def get_max_day(grouped_df):
    return grouped_df.loc[grouped_df["count"].idxmax()]


maxday = daily_counts.groupby("pnum", as_index=False).apply(get_max_day)
maxday["maxday"] = pd.to_datetime(maxday["date"])
maxday["lay_date"] = pd.to_datetime(maxday["lay_date"])
maxday["days_from_lay"] = (maxday["maxday"] - maxday["lay_date"]).dt.days

# plot the distribution of days_from_lay (kde + histogram)
fig, ax = plt.subplots(figsize=(figwidth, figwidth / 2))
sns.histplot(data=maxday["days_from_lay"], ax=ax, bins=10 + 6, discrete=True)
# add a vertical line at 0 days
ax.axvline(0, color="red", linestyle="--")

ax.set_xlim(-11, 6)
ax.set_xticks(range(-11, 7))
ax.set_xticklabels(range(-11, 7))
ax.set_xlabel("Days from first egg")
ax.set_ylabel("Density")
plt.tight_layout()


# are the manual segmentations correlated with the number of detections using
# BirdNET?

samplingcorr = daily_counts.groupby("pnum", as_index=False).agg({"count": "sum", "n_vocalisations": "first"})
# join and plot the relationship between total detections and n_vocalizations
fig, ax = plt.subplots(figsize=(figwidth, figwidth))

# add a scatterplot with log axes
sns.scatterplot(data=samplingcorr, y="count", x="n_vocalisations", ax=ax)
ax.set_xscale("log")
ax.set_yscale("log")
# add a diagonal line
ax.plot([1, 1e4], [1, 1e4], color="#5fa389", linestyle="--")
# add a grid
ax.grid(True)
ax.set_xlabel("N Songs (manual)")
ax.set_ylabel("N Detections (automated)")
plt.tight_layout()
plt.show()


# Get the subset of pnums where the first day of detection is three days before
# the lay date or earlier, and the last day of detection is at least 1 day after
# the lay date.
subset_pnums = daily_counts.groupby("pnum").filter(
    lambda x: (-10 <= x["days_from_lay"].min() <= -3) and (1 <= x["days_from_lay"].max() <= 10)
)

# for each unique pnum count how many days there are detections for
n_pnums = subset_pnums.groupby("pnum", as_index=False).agg({"days_from_lay": "count"})


# for each unique pnum, plot the number of detections per day, with date centred
# around the lay date (days from lay)
fig, ax = plt.subplots(figsize=(15, figwidth))
for pnum, group in subset_pnums.groupby("pnum"):
    group = group.copy()
    group["days_from_lay"] = group["days_from_lay"] + 3
    group["scaled_count"] = group["count"] / group["count"].max()  # Scale counts to the same range
    ax.plot(group["days_from_lay"], group["scaled_count"], label=pnum)

ax.set_xlabel("Days from Lay Date")
ax.set_ylabel("Scaled Number of Detections")
ax.set_title("Detections per day, centred around lay date (scaled)")
plt.tight_layout()
plt.show()

# Plot the distribution of peaks in song activity in this subset
fig, ax = plt.subplots(figsize=(figwidth, figwidth / 2))
maxday_subset = subset_pnums.groupby("pnum", as_index=False).apply(get_max_day)
maxday_subset["maxday"] = pd.to_datetime(maxday_subset["date"])
sns.histplot(data=maxday_subset["days_from_lay"], ax=ax, bins=10 + 6, discrete=True)
ax.set_xlim(-11, 6)
ax.set_xticks(range(-11, 7))
ax.set_xticklabels(range(-11, 7))
ax.set_xlabel("Days from first egg")
ax.set_ylabel("Density")
plt.tight_layout()
plt.show()
