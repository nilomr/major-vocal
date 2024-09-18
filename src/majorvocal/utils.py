import json
from pathlib import Path

import pandas as pd
from tqdm import tqdm


def extract_parus_major(data: list[list[str, str, list[dict]]]) -> list[dict]:
    """
    Extracts detections of Parus major from the given data. For each recording,
    the function checks if there is a detection of Parus major. If there is, it
    extracts the timestamp, recording ID, start time, end time, and confidence
    level of the detection. If there is no detection of Parus major, it adds
    a dictionary with the timestamp, recording ID, start time, end time, and
    confidence level as None.

    Args:
        data (List[List[str, str, List[dict]]]): A list of recordings, where each recording is a list
                     containing the timestamp, recording ID, and a list of dictionaries
                     containing the detections.

    Returns:
        List[dict]: A list of dictionaries representing the Parus major detections. Each
              dictionary contains the timestamp, recording ID, start time, end time,
              and confidence level of the detection.
    """
    parus_major_detections = []

    for recording in tqdm(data, desc="Extracting Parus Major Detections"):
        timestamp, recording_id, detections = recording
        n_pmajor = 0
        for detection in detections:
            if detection["scientific_name"] == "Parus major":
                parus_major_detections.append(
                    {
                        "timestamp": timestamp,
                        "pnum": recording_id,
                        "date": timestamp.split("_")[0],
                        "start_time": detection["start_time"],
                        "end_time": detection["end_time"],
                        "confidence": detection["confidence"],
                    }
                )
                n_pmajor += 1
        if n_pmajor == 0:
            parus_major_detections.append(
                {
                    "timestamp": timestamp,
                    "pnum": recording_id,
                    "date": timestamp.split("_")[0],
                    "start_time": None,
                    "end_time": None,
                    "confidence": None,
                }
            )

    return parus_major_detections


def to_df(pmajor: list[dict]) -> pd.DataFrame:
    df = pd.DataFrame(pmajor)
    df["date"] = pd.to_datetime(df["date"], format="%Y%m%d")
    df["start_datetime"] = pd.to_datetime(df["timestamp"], format="%Y%m%d_%H%M%S") + pd.to_timedelta(
        df["start_time"], unit="s"
    )
    df["end_datetime"] = pd.to_datetime(df["timestamp"], format="%Y%m%d_%H%M%S") + pd.to_timedelta(
        df["end_time"], unit="s"
    )
    df["location"] = df["pnum"].str[5:]
    df["year"] = df["start_datetime"].dt.year
    df["dayofyear"] = df["start_datetime"].dt.dayofyear
    return df
