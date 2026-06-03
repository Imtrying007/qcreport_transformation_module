import os
import pandas as pd

def run_img_selection_summary(run_dir, df):

    print("Starting Image Selection Summary Pipeline...")
    print("-" * 40)

    output_path = os.path.join(run_dir, "img_selection_summary.csv")

    # -----------------------------------------
    # Safety + normalization
    # -----------------------------------------
    df = df.copy()

    df["shop_name"] = df["shop_name"].fillna("").astype(str)
    df["category_name"] = df["category_name"].fillna("").astype(str)
    df["file_path"] = df["file_path"].fillna("").astype(str)

    # -----------------------------------------
    # Extract date from shop_name
    # -----------------------------------------
    df["date"] = df["shop_name"].str.extract(r"(\d{4}-\d{2}-\d{2})")

    # Remove invalid dates
    df = df.dropna(subset=["date"])

    # -----------------------------------------
    # REMOVE DUPLICATES (core fix)
    # keep only unique file_path per category per date
    # -----------------------------------------
    df = df.drop_duplicates(subset=["category_name", "date", "file_path"])

    # -----------------------------------------
    # Count unique images
    # -----------------------------------------
    img_summary = (
        df.groupby(["category_name", "date"])
        .size()
        .reset_index(name="img_counts")
    )

    # -----------------------------------------
    # Final format
    # -----------------------------------------
    img_summary = img_summary[
        ["category_name", "date", "img_counts"]
    ]

    # -----------------------------------------
    # Save output
    # -----------------------------------------
    img_summary.to_csv(output_path, index=False)

    print("img_selection_summary.csv created successfully")
    print("-" * 40)