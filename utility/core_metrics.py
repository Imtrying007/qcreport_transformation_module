import numpy as np
import pandas as pd


def compute_core_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standard metric engine for all pipelines.

    Expected columns:
        self_count
        comp_count
        others_self
        others_comp
        incorrect_self
        incorrect_comp
        incorrect_others_self
        incorrect_others_comp
    """

    df = df.copy()

    # -----------------------------------------
    # DERIVED COLUMNS
    # -----------------------------------------
    df["others_count"] = df["others_self"] + df["others_comp"]

    df["incorrect_others"] = (
        df["incorrect_others_self"] +
        df["incorrect_others_comp"]
    )

    # -----------------------------------------
    # TOTALS
    # -----------------------------------------
    df["total_count"] = (
        df["self_count"] +
        df["comp_count"] +
        df["others_count"]
    )

    df["total_incorrect"] = (
        df["incorrect_self"] +
        df["incorrect_comp"] +
        df["incorrect_others"]
    )

    # -----------------------------------------
    # SAFE METRICS
    # -----------------------------------------
    df["SPI"] = np.where(
        df["self_count"] > 0,
        (df["self_count"] - df["incorrect_self"]) / df["self_count"],
        np.nan
    )

    df["CPI"] = np.where(
        df["comp_count"] > 0,
        (df["comp_count"] - df["incorrect_comp"]) / df["comp_count"],
        np.nan
    )

    df["NPD"] = np.where(
        df["total_count"] > 0,
        df["others_count"] / df["total_count"],
        np.nan
    )

    df["accuracy"] = np.where(
        df["total_count"] > 0,
        (df["total_count"] - df["total_incorrect"]) / df["total_count"],
        np.nan
    )

    return df