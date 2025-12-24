import pandas as pd
import io
import numpy as np
from scipy.stats import zscore

def generate_summary_statistics(df: pd.DataFrame) -> dict:
    """
    Generates a lightweight dictionary of summary statistics from a Pandas DataFrame.
    """
    summary_stats = {
        "overall_summary": {
            "row_count": len(df),
            "column_count": len(df.columns),
            "missing_values_summary": df.isnull().sum().to_dict(),
            "data_types_distribution": df.dtypes.astype(str).value_counts().to_dict(),
        },
        "numeric_columns": {}
    }

    for col in df.select_dtypes(include=np.number).columns:
        description = df[col].describe().to_dict()
        col_stats = {
            "mean": description.get("mean"),
            "median": df[col].median(),
            "std_dev": description.get("std"),
            "min": description.get("min"),
            "max": description.get("max"),
            "25_percentile": description.get("25%"),
            "75_percentile": description.get("75%"),
        }
        
        # Simple trend indicator: change from min to max
        if not pd.isna(col_stats["min"]) and not pd.isna(col_stats["max"]):
            col_stats["trend_indicator_min_max_delta"] = col_stats["max"] - col_stats["min"]
            if col_stats["min"] != 0:
                col_stats["trend_indicator_min_max_percentage"] = (col_stats["max"] - col_stats["min"]) / col_stats["min"] * 100

        # --- FIX STARTS HERE ---
        # Anomaly detection: Manual Z-score calculation to handle NaNs safely
        std_dev = df[col].std()
        mean_val = df[col].mean()
        
        if std_dev > 0: # Avoid division by zero
            # Calculate Z-score using Pandas (preserves index alignment)
            # (Value - Mean) / StdDev
            z_scores = (df[col] - mean_val) / std_dev
            
            # Filter for outliers (|Z| > 3)
            outliers = df[col][z_scores.abs() > 3].dropna().tolist()
            
            col_stats["anomaly_detection_zscore_outliers_count"] = len(outliers)
            col_stats["anomaly_detection_zscore_outliers_examples"] = outliers[:5] 
        # --- FIX ENDS HERE ---

        summary_stats["numeric_columns"][col] = col_stats
    
    # Add non-numeric column value counts for context
    summary_stats["non_numeric_columns"] = {}
    for col in df.select_dtypes(exclude=np.number).columns:
        summary_stats["non_numeric_columns"][col] = df[col].value_counts().head(5).to_dict()

    return summary_stats

def process_csv(file_buffer: io.BytesIO) -> dict:
    """
    Ingests CSV data from a file-like object, processes it, and generates summary statistics.

    Args:
        file_buffer: A file-like object containing the CSV data.

    Returns:
        A dictionary containing summary statistics suitable for LLM context.

    Raises:
        ValueError: If the file buffer is empty.
        pd.errors.EmptyDataError: If the CSV file is empty or unparseable.
        Exception: For other CSV parsing errors.
    """
    if not file_buffer:
        raise ValueError("File buffer is empty.")

    try:
        file_buffer.seek(0)
        df = pd.read_csv(file_buffer)
        return generate_summary_statistics(df)
    except pd.errors.EmptyDataError:
        raise pd.errors.EmptyDataError("The provided CSV file is empty or unparseable.")
    except Exception as e:
        raise Exception(f"Error processing CSV file: {e}")