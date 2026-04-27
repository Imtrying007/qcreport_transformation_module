import pandas as pd
import numpy as np
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utility.grading import assign_grade
from utility.recommendation import assign_recommendation



def run_summary(run_dir):

    print("Starting Summary Pipeline...")
    print("-" * 40)

    input_path = os.path.join(run_dir, "analytic.csv")
    output_path = os.path.join(run_dir, "summary.csv")

    # -----------------------------------------
    # Load data
    # -----------------------------------------
    agg_df = pd.read_csv(input_path)
    print("Data loaded successfully")

    # -----------------------------------------
    # Normalize text columns
    # -----------------------------------------
    agg_df['qc_class_name'] = agg_df['qc_class_name'].astype(str).str.lower()
    agg_df['qc_competition'] = agg_df['qc_competition'].astype(str).str.lower()
    agg_df['category_name'] = agg_df['category_name'].astype(str)

    # -----------------------------------------
    # Vectorized flags
    # -----------------------------------------
    self_flag = agg_df['qc_competition'] == 'self'
    comp_flag = agg_df['qc_competition'] == 'competitor'
    sticker_flag = agg_df['qc_class_name'].str.contains('sticker', na=False)
    others_flag = agg_df['qc_class_name'].str.contains('other', na=False)
    incorrect_flag = agg_df['ai_correct'] == False

    print("Flags created")

    # -----------------------------------------
    # Grouping
    # -----------------------------------------
    group_cols_cat = ['category_id', 'category_name']

    cat_agg = agg_df.groupby(group_cols_cat).agg(
        total_image_count=('test_image_id', 'nunique'),
        self_count=('qc_competition',
                    lambda x: (self_flag.loc[x.index]).sum()
                              - (self_flag.loc[x.index] & sticker_flag.loc[x.index]).sum()),
        comp_count=('qc_competition',
                    lambda x: (comp_flag.loc[x.index]).sum()
                              - (comp_flag.loc[x.index] & sticker_flag.loc[x.index]).sum()
                              - (comp_flag.loc[x.index] & others_flag.loc[x.index]).sum()),
        others_count=('qc_class_name',
                      lambda x: (comp_flag.loc[x.index] & others_flag.loc[x.index]).sum()),
        sticker_count=('qc_class_name',
                       lambda x: sticker_flag.loc[x.index].sum()),
        incorrect_self=('qc_competition',
                        lambda x: (self_flag.loc[x.index] & incorrect_flag.loc[x.index]).sum()),
        incorrect_comp=('qc_competition',
                        lambda x: (comp_flag.loc[x.index]
                                   & incorrect_flag.loc[x.index]
                                   & ~sticker_flag.loc[x.index]
                                   & ~others_flag.loc[x.index]).sum()),
        incorrect_others=('qc_class_name',
                          lambda x: (others_flag.loc[x.index] & incorrect_flag.loc[x.index]).sum())
    ).reset_index()

    print("Category aggregation completed")

    # -----------------------------------------
    # Metrics
    # -----------------------------------------
    cat_agg['SPI'] = (cat_agg['self_count'] - cat_agg['incorrect_self']) / cat_agg['self_count']
    cat_agg['CPI'] = (cat_agg['comp_count'] - cat_agg['incorrect_comp']) / cat_agg['comp_count']
    cat_agg['NPD'] = cat_agg['others_count'] / (
        cat_agg['self_count'] + cat_agg['comp_count'] + cat_agg['others_count']
    )
    cat_agg['total_count'] = cat_agg['self_count'] + cat_agg['comp_count'] + cat_agg['others_count']
    cat_agg['total_incorrect'] = cat_agg['incorrect_self'] + cat_agg['incorrect_comp'] + cat_agg['incorrect_others']
    cat_agg['accuracy'] = (cat_agg['total_count'] - cat_agg['total_incorrect']) / cat_agg['total_count']

    print("Metrics calculated")

    # -----------------------------------------
    # AI Grade
    # -----------------------------------------
    F = cat_agg['accuracy']
    G = cat_agg['SPI']
    H = cat_agg['NPD']
    not_blank = (~F.isna()) & (~G.isna()) & (~H.isna())
    cat_agg['Ai_grade'] = ""
    cat_agg = assign_grade(cat_agg, F, G, H)
    print("AI grading completed")

    # -----------------------------------------
    # Recommendation
    # -----------------------------------------
    cat_agg['recommendation'] = ""
    cat_agg = assign_recommendation(cat_agg, F, G, H)
    print("Recommendations added")

    # -----------------------------------------
    # TOTAL Row (Overall Summary)
    # -----------------------------------------
    total_row = {}
    sum_cols = [
        'total_image_count', 'self_count', 'comp_count', 'others_count',
        'sticker_count', 'incorrect_self', 'incorrect_comp', 'incorrect_others',
        'total_count', 'total_incorrect'
    ]
    for col in sum_cols:
        total_row[col] = cat_agg[col].sum()

    total_row['category_id'] = ""
    total_row['category_name'] = "OVERALL"

    self_count = total_row['self_count']
    comp_count = total_row['comp_count']
    others_count = total_row['others_count']
    total_count = total_row['total_count']
    total_incorrect = total_row['total_incorrect']
    incorrect_self = total_row['incorrect_self']
    incorrect_comp = total_row['incorrect_comp']

    total_row['SPI'] = (self_count - incorrect_self) / self_count if self_count != 0 else np.nan
    total_row['CPI'] = (comp_count - incorrect_comp) / comp_count if comp_count != 0 else np.nan
    total_row['NPD'] = others_count / (self_count + comp_count + others_count) if (self_count + comp_count + others_count) != 0 else np.nan
    total_row['accuracy'] = (total_count - total_incorrect) / total_count if total_count != 0 else np.nan

    # Apply grading + recommendation
    total_df = pd.DataFrame([total_row])
    total_df = assign_grade(total_df, total_df['accuracy'], total_df['SPI'], total_df['NPD'])
    total_df = assign_recommendation(total_df, total_df['accuracy'], total_df['SPI'], total_df['NPD'])
    total_row = total_df.iloc[0].to_dict()

    # Append TOTAL row at the END
    cat_agg = pd.concat([cat_agg, pd.DataFrame([total_row])], ignore_index=True)

    # -----------------------------------------
    # Column Order
    # -----------------------------------------
    cat_agg = cat_agg[
        [
            'category_id', 'category_name', 'total_image_count', 'self_count',
            'comp_count', 'others_count', 'sticker_count', 'incorrect_self',
            'incorrect_comp', 'incorrect_others', 'SPI', 'CPI', 'NPD',
            'total_count', 'total_incorrect', 'accuracy', 'Ai_grade', 'recommendation'
        ]
    ]

    # -----------------------------------------
    # Save CSV
    # -----------------------------------------
    cat_agg.to_csv(output_path, index=False)
    print("summary.csv created successfully")
    print("-" * 40)


# ----------------------------------------
# Entry Point
# ----------------------------------------
# if __name__ == "__main__":
#     run_summary(os.cwd())