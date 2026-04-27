import pandas as pd
import os

# -----------------------------------------
# Paths
# -----------------------------------------

# -----------------------------------------
# Notes Pipeline
# -----------------------------------------
def run_notes(run_dir):

    print("Starting Notes Pipeline...")
    print("-" * 40)

    input_path = os.path.join(run_dir, "analytic.csv")
    output_path = os.path.join(run_dir, "notes.csv")

    # -----------------------------------------
    # Load data
    # -----------------------------------------
    df = pd.read_csv(input_path)
    print("analytic.csv loaded successfully")

    # -----------------------------------------
    # Filter ai_correct = False
    # -----------------------------------------
    false_df = df[df["ai_correct"] == False]
    print(f"Total incorrect rows: {len(false_df)}")

    # -----------------------------------------
    # Grouping
    # -----------------------------------------
    result = (
        false_df
        .groupby(["category_id", "category_name","qc_class_id", "qc_class_name", "class_name","class_id"])
        .size()
        .reset_index(name="count")
    )

    # -----------------------------------------
    # Add total per category
    # -----------------------------------------
    result["total_count"] = result.groupby("category_name")["count"].transform("sum")

    # -----------------------------------------
    # Add ratio column (rounded decimal)
    # -----------------------------------------
    result["category_ratio"] = (
        result["count"] / result["total_count"]
    ).round(4)

    # Adding image url with max error of that particular type
        # -----------------------------------------
    # Adding image url with max error of that particular type
    # -----------------------------------------

    # Count errors per image for each (category, actual, predicted)
    file_level = (
        false_df
        .groupby([
            "category_id",
            "category_name",
            "qc_class_id",
            "qc_class_name",
            "class_name",
            "class_id",
            "file_path"
        ])
        .size()
        .reset_index(name="case_count")
    )

    # Pick the image with maximum errors per (category, actual, predicted)
    max_file_df = file_level.loc[
        file_level.groupby(
            ["category_id", "category_name","qc_class_id", "qc_class_name", "class_name","class_id"]
        )["case_count"].idxmax()
    ]

    # Merge into main result
    result = result.merge(
        max_file_df,
        on=["category_id", "category_name","qc_class_id", "qc_class_name", "class_name","class_id"],
        how="left"
    )
        # -----------------------------------------
    # Add actual_present (correct predictions count)
    # -----------------------------------------

    actual_present_df = (
        df
        .groupby([
            "category_id",
            "category_name",
            "qc_class_id",
            "qc_class_name"
        ])
        .size()
        .reset_index(name="actual_present")
    )

    # Merge into result
    result = result.merge(
        actual_present_df,
        on=["category_id", "category_name", "qc_class_id", "qc_class_name"],
        how="left"
    )

    # Fill NaN (cases where no correct predictions exist)
    result["actual_present"] = result["actual_present"].fillna(0).astype(int)
    # rename the columns
    result = result.rename(columns={
        "qc_class_name": "actual",
        "class_name": "predicted"
    })

    # -----------------------------------------
    # Sorting
    # -----------------------------------------
    result = result.sort_values(
        ["category_name", "count"],
        ascending=[True, False]
    )

    print("Notes aggregation completed")

    # -----------------------------------------
    # Save CSV
    # -----------------------------------------
    result.to_csv(output_path, index=False)

    print("notes.csv created successfully")
    print("-" * 40)


# -----------------------------------------
# Entry Point
# -----------------------------------------
# if __name__ == "__main__":
#     run_notes(os.cwd())