import pandas as pd
import numpy as np
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utility.grading import assign_grade


# -----------------------------------------
# Image Level Pipeline
# -----------------------------------------
def run_image_level(run_dir):
    print("Starting Image Level Pipeline...")
    print("-" * 40)

    input_path = os.path.join(run_dir, "analytic.csv")
    output_path = os.path.join(run_dir, "image_wise.csv")

    # -----------------------------------------
    # Load data
    # -----------------------------------------
    df = pd.read_csv(input_path)
    print("analytic.csv loaded successfully")

    # -----------------------------------------
    # Normalize
    # -----------------------------------------
    df["qc_class_name"] = df["qc_class_name"].astype(str).str.lower()
    df["qc_competition"] = df["qc_competition"].astype(str).str.lower()

    # -----------------------------------------
    # Base flags
    # -----------------------------------------
    self_flag = df["qc_competition"].eq("self")
    comp_flag = df["qc_competition"].eq("competitor")

    others_flag = df["qc_class_name"].str.contains("other", na=False)
    sticker_raw = df["qc_class_name"].str.contains("sticker", na=False)

    incorrect_flag = df["ai_correct"].eq(False)
    sticker_flag = sticker_raw & df["ai_correct"].isna()

    exclude_sticker = sticker_flag

    # -----------------------------------------
    # PURE buckets
    # -----------------------------------------
    pure_self = self_flag & ~others_flag & ~exclude_sticker
    pure_comp = comp_flag & ~others_flag & ~exclude_sticker

    # -----------------------------------------
    # OTHERS split
    # -----------------------------------------
    others_self = others_flag & self_flag
    others_comp = others_flag & comp_flag

    # -----------------------------------------
    # Grouping
    # -----------------------------------------
    group_cols = [
        "category_id",
        "category_name",
        "capture_date",
        "shop_id",
        "test_image_id",
        "file_path",
    ]

    # -----------------------------------------
    # Aggregation
    # -----------------------------------------
    img_agg = df.groupby(group_cols).agg(

        self_count=("qc_competition", lambda x: pure_self.loc[x.index].sum()),
        comp_count=("qc_competition", lambda x: pure_comp.loc[x.index].sum()),

        others_self=("qc_class_name", lambda x: others_self.loc[x.index].sum()),
        others_comp=("qc_class_name", lambda x: others_comp.loc[x.index].sum()),

        sticker_count=("qc_class_name", lambda x: sticker_flag.loc[x.index].sum()),

        incorrect_self=("qc_competition",
            lambda x: (pure_self.loc[x.index] & incorrect_flag.loc[x.index]).sum()
        ),

        incorrect_comp=("qc_competition",
            lambda x: (pure_comp.loc[x.index] & incorrect_flag.loc[x.index]).sum()
        ),

        incorrect_others_self=("qc_class_name",
            lambda x: (others_self.loc[x.index] & incorrect_flag.loc[x.index]).sum()
        ),

        incorrect_others_comp=("qc_class_name",
            lambda x: (others_comp.loc[x.index] & incorrect_flag.loc[x.index]).sum()
        ),
    ).reset_index()

    print("Image level aggregation completed")

    # -----------------------------------------
    # Metrics (safe)
    # -----------------------------------------
    img_agg["total_count"] = (
        img_agg["self_count"]
        + img_agg["comp_count"]
        + img_agg["others_self"]
        + img_agg["others_comp"]
    )

    img_agg["total_incorrect"] = (
        img_agg["incorrect_self"]
        + img_agg["incorrect_comp"]
        + img_agg["incorrect_others_self"]
        + img_agg["incorrect_others_comp"]
    )

    # Safe divisions
    img_agg["accuracy"] = np.where(
        img_agg["total_count"] > 0,
        (img_agg["total_count"] - img_agg["total_incorrect"]) / img_agg["total_count"],
        np.nan,
    )

    img_agg["SPI"] = np.where(
        img_agg["self_count"] > 0,
        (img_agg["self_count"] - img_agg["incorrect_self"]) / img_agg["self_count"],
        np.nan,
    )

    img_agg["CPI"] = np.where(
        img_agg["comp_count"] > 0,
        (img_agg["comp_count"] - img_agg["incorrect_comp"]) / img_agg["comp_count"],
        np.nan,
    )

    img_agg["NPD"] = np.where(
        img_agg["total_count"] > 0,
        (img_agg["others_self"] + img_agg["others_comp"]) / img_agg["total_count"],
        np.nan,
    )

    print("Metrics calculated")

    # -----------------------------------------
    # AI Grade
    # -----------------------------------------
    img_agg = assign_grade(
        img_agg,
        img_agg["accuracy"],
        img_agg["SPI"],
        img_agg["NPD"],
    )

    print("AI grading completed")

    # -----------------------------------------
    # Final output
    # -----------------------------------------
    final_cols = [
        "category_id",
        "category_name",
        "capture_date",
        "shop_id",
        "file_path",
        "test_image_id",
        "self_count",
        "comp_count",
        "others_self",
        "others_comp",
        "sticker_count",
        "incorrect_self",
        "incorrect_comp",
        "incorrect_others_self",
        "incorrect_others_comp",
        "SPI",
        "CPI",
        "NPD",
        "total_count",
        "total_incorrect",
        "accuracy",
        "Ai_grade",
    ]

    img_agg[final_cols].to_csv(output_path, index=False)

    print("image_wise.csv created successfully")
    print("-" * 40)