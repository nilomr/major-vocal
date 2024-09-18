import pandas as pd
import pytest

from majorvocal.utils import extract_parus_major, to_df


@pytest.fixture
def sample_data():
    return [
        [
            "20220101_000000",
            "recording1",
            [
                {"scientific_name": "Parus major", "start_time": 10, "end_time": 20, "confidence": 0.9},
                {"scientific_name": "Parus minor", "start_time": 30, "end_time": 40, "confidence": 0.8},
            ],
        ],
        [
            "20220102_000000",
            "recording2",
            [
                {"scientific_name": "Parus major", "start_time": 5, "end_time": 15, "confidence": 0.7},
                {"scientific_name": "Parus major", "start_time": 25, "end_time": 35, "confidence": 0.6},
                {"scientific_name": "Parus minor", "start_time": 45, "end_time": 55, "confidence": 0.5},
            ],
        ],
        # Add more sample data as needed
    ]


def test_extract_parus_major(sample_data):
    expected_output = [
        {"timestamp": "20220101_000000", "pnum": "recording1", "start_time": 10, "end_time": 20, "confidence": 0.9},
        {"timestamp": "20220102_000000", "pnum": "recording2", "start_time": 5, "end_time": 15, "confidence": 0.7},
        {"timestamp": "20220102_000000", "pnum": "recording2", "start_time": 25, "end_time": 35, "confidence": 0.6},
    ]

    result = extract_parus_major(sample_data)
    assert result == expected_output


def test_to_df():
    pmajor = [
        {"timestamp": "20220101_000000", "pnum": "20201EX26", "start_time": 10, "end_time": 20, "confidence": 0.9},
        {"timestamp": "20220102_000000", "pnum": "20201EX66", "start_time": 5, "end_time": 15, "confidence": 0.7},
        {"timestamp": "20220102_000000", "pnum": "20201EX268", "start_time": 25, "end_time": 35, "confidence": 0.6},
    ]
    expected_output = pd.DataFrame(
        {
            "timestamp": ["20220101_000000", "20220102_000000", "20220102_000000"],
            "pnum": ["20201EX26", "20201EX66", "20201EX268"],
            "start_time": [10, 5, 25],
            "end_time": [20, 15, 35],
            "confidence": [0.9, 0.7, 0.6],
            "start_datetime": [
                pd.to_datetime("20220101_000000", format="%Y%m%d_%H%M%S") + pd.to_timedelta(10, unit="s"),
                pd.to_datetime("20220102_000000", format="%Y%m%d_%H%M%S") + pd.to_timedelta(5, unit="s"),
                pd.to_datetime("20220102_000000", format="%Y%m%d_%H%M%S") + pd.to_timedelta(25, unit="s"),
            ],
            "end_datetime": [
                pd.to_datetime("20220101_000000", format="%Y%m%d_%H%M%S") + pd.to_timedelta(20, unit="s"),
                pd.to_datetime("20220102_000000", format="%Y%m%d_%H%M%S") + pd.to_timedelta(15, unit="s"),
                pd.to_datetime("20220102_000000", format="%Y%m%d_%H%M%S") + pd.to_timedelta(35, unit="s"),
            ],
            "location": ["EX26", "EX66", "EX268"],
            "year": [2022, 2022, 2022],
            "dayofyear": [1, 2, 2],
        }
    ).astype({"year": "int32", "dayofyear": "int32"})

    result = to_df(pmajor)
    pd.testing.assert_frame_equal(result, expected_output)
