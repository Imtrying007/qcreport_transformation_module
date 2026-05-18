import pandas as pd
import os

# -----------------------------------------
# Paths
# -----------------------------------------

# -----------------------------------------
# Notes_g Pipeline
# -----------------------------------------
def run_notes_g(run_dir, df):

    print("Starting Notes_g Pipeline will be used for ingestion if and only if class_name is others and group name has some brand...")
    print("-" * 40)

    output_path = os.path.join(run_dir, "notes2.csv")

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
        .groupby([
            "category_id",
            "category_name",

            # Actual labels
            "qc_group_id",
            "qc_group_name",
            "qc_class_id",
            "qc_class_name",

            # Predicted labels
            "group_id",
            "group_name",
            "class_id",
            "class_name"
        ])
        .size()
        .reset_index(name="count")
    )

    # -----------------------------------------
    # Add total per category
    # -----------------------------------------
    result["total_count"] = (
        result.groupby("category_name")["count"]
        .transform("sum")
    )

    # -----------------------------------------
    # Add ratio column
    # -----------------------------------------
    result["category_ratio"] = (
        result["count"] / result["total_count"]
    ).round(4)

    # -----------------------------------------
    # Count errors per image
    # -----------------------------------------
    file_level = (
        false_df
        .groupby([
            "category_id",
            "category_name",

            # Actual labels
            "qc_group_id",
            "qc_group_name",
            "qc_class_id",
            "qc_class_name",

            # Predicted labels
            "group_id",
            "group_name",
            "class_id",
            "class_name",

            "file_path"
        ])
        .size()
        .reset_index(name="case_count")
    )

    # -----------------------------------------
    # Pick image with max errors
    # -----------------------------------------
    max_file_df = file_level.loc[
        file_level.groupby([
            "category_id",
            "category_name",

            # Actual labels
            "qc_group_id",
            "qc_group_name",
            "qc_class_id",
            "qc_class_name",

            # Predicted labels
            "group_id",
            "group_name",
            "class_id",
            "class_name"
        ])["case_count"].idxmax()
    ]

    # -----------------------------------------
    # Merge file-level info
    # -----------------------------------------
    result = result.merge(
        max_file_df,
        on=[
            "category_id",
            "category_name",

            # Actual labels
            "qc_group_id",
            "qc_group_name",
            "qc_class_id",
            "qc_class_name",

            # Predicted labels
            "group_id",
            "group_name",
            "class_id",
            "class_name"
        ],
        how="left"
    )

    # -----------------------------------------
    # Add actual_present
    # -----------------------------------------
    actual_present_df = (
        df
        .groupby([
            "category_id",
            "category_name",

            # Actual labels
            "qc_group_id",
            "qc_group_name",
            "qc_class_id",
            "qc_class_name"
        ])
        .size()
        .reset_index(name="actual_present")
    )

    # -----------------------------------------
    # Merge actual_present
    # -----------------------------------------
    result = result.merge(
        actual_present_df,
        on=[
            "category_id",
            "category_name",
            "qc_group_id",
            "qc_group_name",
            "qc_class_id",
            "qc_class_name"
        ],
        how="left"
    )

    # -----------------------------------------
    # Fill NaN values
    # -----------------------------------------
    result["actual_present"] = (
        result["actual_present"]
        .fillna(0)
        .astype(int)
    )
    # -----------------------------------------
    # Ensure required predicted id columns exist
    # (from file_level merge they should already be present)
    # -----------------------------------------
    if "group_id" not in result.columns:
        result["group_id"] = None

    if "class_id" not in result.columns:
        result["class_id"] = None

    # -----------------------------------------
    # Rename columns
    # -----------------------------------------
    result = result.rename(columns={

        # Actual
        "qc_group_id": "actual_group_id",
        "qc_group_name": "actual_group",
        "qc_class_id": "actual_class_id",
        "qc_class_name": "actual_class",

        # Predicted
        "group_id": "predicted_group_id",
        "group_name": "predicted_group",
        "class_id": "predicted_class_id",
        "class_name": "predicted_class"

    })


    # -----------------------------------------
    # Reorder columns (FINAL SCHEMA)
    # -----------------------------------------
    result = result[[
        "category_id",
        "category_name",

        "actual_group_id",

        "actual_group",
        "actual_class",
        "actual_class_id",

        "predicted_group",
        "predicted_group_id",
        "predicted_class",
        "predicted_class_id",

        "count",
        "total_count",
        "category_ratio",

        "file_path",
        "case_count",
        "actual_present"
    ]]
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

    print("notes2.csv created successfully")
    print("-" * 40)


# -----------------------------------------
# Entry Point
# -----------------------------------------
# if __name__ == "__main__":
#     run_notes_g(os.cwd())