import pytest
import pandas as pd
import io
import numpy as np
from ai_report_generator.src.data_processor import process_csv, generate_summary_statistics

# --- Tests for generate_summary_statistics ---

def test_generate_summary_statistics_basic():
    data = {'col1': [1, 2, 3, 4, 5], 'col2': [10, 20, 30, 40, 50]}
    df = pd.DataFrame(data)
    stats = generate_summary_statistics(df)

    assert stats['overall_summary']['row_count'] == 5
    assert stats['overall_summary']['column_count'] == 2
    assert stats['numeric_columns']['col1']['mean'] == 3.0
    assert stats['numeric_columns']['col2']['max'] == 50.0
    assert 'trend_indicator_min_max_delta' in stats['numeric_columns']['col1']

def test_generate_summary_statistics_with_nans():
    data = {'col1': [1, 2, np.nan, 4, 5], 'col2': [10, np.nan, 30, 40, 50]}
    df = pd.DataFrame(data)
    stats = generate_summary_statistics(df)

    assert stats['overall_summary']['missing_values_summary']['col1'] == 1
    assert stats['overall_summary']['missing_values_summary']['col2'] == 1
    assert stats['numeric_columns']['col1']['mean'] == pytest.approx(3.0, 0.01) # mean ignores NaN
    assert stats['numeric_columns']['col2']['median'] == 40.0 # median ignores NaN

def test_generate_summary_statistics_non_numeric():
    data = {'category': ['A', 'B', 'A', 'C', 'B'], 'value': [1, 2, 3, 4, 5]}
    df = pd.DataFrame(data)
    stats = generate_summary_statistics(df)

    assert 'category' in stats['non_numeric_columns']
    assert stats['non_numeric_columns']['category']['A'] == 2

def test_generate_summary_statistics_anomalies():
    data = {'sales': [10, 12, 11, 100, 13, 11]} # 100 is an outlier
    df = pd.DataFrame(data)
    stats = generate_summary_statistics(df)

    assert stats['numeric_columns']['sales']['anomaly_detection_zscore_outliers_count'] >= 1
    assert 100.0 in stats['numeric_columns']['sales']['anomaly_detection_zscore_outliers_examples']


# --- Tests for process_csv ---

def test_process_csv_valid_file():
    csv_content = "col1,col2\n1,10\n2,20\n3,30"
    file_buffer = io.BytesIO(csv_content.encode('utf-8'))
    stats = process_csv(file_buffer)

    assert stats['overall_summary']['row_count'] == 3
    assert stats['numeric_columns']['col1']['mean'] == 2.0

def test_process_csv_empty_file():
    csv_content = ""
    file_buffer = io.BytesIO(csv_content.encode('utf-8'))
    with pytest.raises(pd.errors.EmptyDataError):
        process_csv(file_buffer)

def test_process_csv_file_with_nans():
    csv_content = "col1,col2\n1,10\n2,\n3,30"
    file_buffer = io.BytesIO(csv_content.encode('utf-8'))
    stats = process_csv(file_buffer)

    assert stats['overall_summary']['row_count'] == 3
    assert stats['overall_summary']['missing_values_summary']['col2'] == 1
    assert stats['numeric_columns']['col1']['mean'] == 2.0

def test_process_csv_only_headers():
    csv_content = "col1,col2"
    file_buffer = io.BytesIO(csv_content.encode('utf-8'))
    stats = process_csv(file_buffer)

    assert stats['overall_summary']['row_count'] == 0
    assert stats['overall_summary']['column_count'] == 2

def test_process_csv_invalid_csv_format():
    csv_content = "col1;col2\n1;10\n2;20" # Semicolon separated, default read_csv expects comma
    file_buffer = io.BytesIO(csv_content.encode('utf-8'))
    # Depending on pandas version and content, this might raise ParserError or return malformed df
    # For this test, we expect some form of error or unexpected behavior,
    # or ensure it doesn't crash but results in appropriate stats.
    # A more specific test would mock pd.read_csv to raise a specific error.
    with pytest.raises((Exception, pd.errors.ParserError)): # Expecting a parsing error
        process_csv(file_buffer)

