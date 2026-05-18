import pandas as pd
import os

# -----------------------------------------
# SKU Level Pipeline
# -----------------------------------------
def run_sku_level(run_dir,df):

    print("Starting SKU Level Pipeline...")
    print("-" * 40)

    output_path = os.path.join(run_dir, "sku_level.csv")

    # -----------------------------------------
    # Filter ai_correct = False
    # -----------------------------------------
    false_df = df[df["ai_correct"] == False]
    print(f"Total incorrect rows: {len(false_df)}")

    # -----------------------------------------
    # 1 & 2:
    # Distinct qc_class_name category wise
    # and incorrect count
    # -----------------------------------------
    result = (
        false_df
        .groupby([
            "category_id",
            "category_name",
            "qc_group_id",
            "qc_group_name",
            "qc_class_id",
            "qc_class_name"
        ])
        .size()
        .reset_index(name="incorrect_count")
    )

    # -----------------------------------------
    # 3:
    # total_actual_present
    # same logic as notes
    # -----------------------------------------
    total_actual_present_df = (
        df
        .groupby([
            "category_id",
            "category_name",
            "qc_group_id",
            "qc_group_name",
            "qc_class_id",
            "qc_class_name"
        ])
        .size()
        .reset_index(name="total_actual_present")
    )

    result = result.merge(
        total_actual_present_df,
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
    # 4:
    # accuracy = 1 - incorrect / total_actual_present
    # -----------------------------------------
    result["accuracy"] = (
        1 -
        (
            result["incorrect_count"] /
            result["total_actual_present"]
        )
    ).round(4)

    # -----------------------------------------
    # 5 & 6:
    # case_count maximum occurrence of
    # qc_class_name where ai_correct=False
    # in a file_path
    # -----------------------------------------
    file_level = (
        false_df
        .groupby([
            "category_id",
            "category_name",
            "qc_group_id",
            "qc_group_name",
            "qc_class_id",
            "qc_class_name",
            "file_path"
        ])
        .size()
        .reset_index(name="case_count")
    )

    # Pick file_path having max occurrence
    max_file_df = file_level.loc[
        file_level.groupby([
            "category_id",
            "category_name",
            "qc_group_id",
            "qc_group_name",
            "qc_class_id",
            "qc_class_name"
        ])["case_count"].idxmax()
    ]

    # Merge into result
    result = result.merge(
        max_file_df,
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

    # rename the columns
    result = result.rename(columns={
        "qc_class_name": "Actual_class_name",
        "qc_class_id" :"Actual_class_id",
        "qc_group_id": "Actual_group_id",
        "qc_group_name" : "Actual_group_name"
    })

    # -----------------------------------------
    # Sorting
    # -----------------------------------------

    result = result.sort_values(
        ["category_name", "incorrect_count"],
        ascending=[True, False]
    )

    # -----------------------------------------
    # Save CSV
    # -----------------------------------------
    result.to_csv(output_path, index=False)

    print("sku_level.csv created successfully")
    print("-" * 40)


# -----------------------------------------
# Entry Point
# -----------------------------------------
# if __name__ == "__main__":
#     run_sku_level(os.getcwd())