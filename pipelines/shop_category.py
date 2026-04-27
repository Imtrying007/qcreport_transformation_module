import pandas as pd
import numpy as np
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utility.grading import assign_grade
from utility.recommendation import assign_recommendation




# -----------------------------------------
# Shop Category Pipeline
# -----------------------------------------
def run_shop_category(run_dir):

    print("Starting Shop Category Pipeline...")
    print("-" * 40)

    input_path = os.path.join(run_dir, "analytic.csv")
    output_path = os.path.join(run_dir, "shopwise.csv")

    # -----------------------------------------
    # Load data
    # -----------------------------------------
    shop_df = pd.read_csv(input_path)
    print("analytic.csv loaded successfully")

    # -----------------------------------------
    # Normalize text columns
    # -----------------------------------------
    shop_df['qc_class_name'] = shop_df['qc_class_name'].astype(str).str.lower()
    shop_df['qc_competition'] = shop_df['qc_competition'].astype(str).str.lower()
    shop_df['category_name'] = shop_df['category_name'].astype(str)

    # -----------------------------------------
    # Vectorized flags
    # -----------------------------------------
    self_flag = shop_df['qc_competition'] == 'self'
    comp_flag = shop_df['qc_competition'] == 'competitor'
    sticker_flag = shop_df['qc_class_name'].str.contains('sticker', na=False)
    others_flag = shop_df['qc_class_name'].str.contains('other', na=False)
    incorrect_flag = shop_df['ai_correct'] == False

    # -----------------------------------------
    # Groupby
    # -----------------------------------------
    group_cols_shop = ['category_id', 'category_name', 'shop_id' ,'capture_date']

    shop_agg = shop_df.groupby(group_cols_shop).agg(

        self_count=('qc_competition',
            lambda x: (
                self_flag.loc[x.index] &
                ~sticker_flag.loc[x.index]
            ).sum()
        ),

        comp_count=('qc_competition',
            lambda x: (
                comp_flag.loc[x.index] &
                ~sticker_flag.loc[x.index] &
                ~others_flag.loc[x.index]
            ).sum()
        ),

        others_count=('qc_class_name',
            lambda x: (
                comp_flag.loc[x.index] &
                others_flag.loc[x.index]
            ).sum()
        ),

        sticker_count=('qc_class_name',
            lambda x: sticker_flag.loc[x.index].sum()
        ),

        incorrect_self=('qc_competition',
            lambda x: (
                self_flag.loc[x.index] &
                incorrect_flag.loc[x.index]
            ).sum()
        ),

        incorrect_comp=('qc_competition',
            lambda x: (
                comp_flag.loc[x.index] &
                incorrect_flag.loc[x.index] &
                ~sticker_flag.loc[x.index] &
                ~others_flag.loc[x.index]
            ).sum()
        ),

        incorrect_others=('qc_class_name',
            lambda x: (
                others_flag.loc[x.index] &
                incorrect_flag.loc[x.index]
            ).sum()
        ),

        total_image_count=('test_image_id', 'nunique')

    ).reset_index()

    print("Shop-level aggregation completed")

    # -----------------------------------------
    # Metrics
    # -----------------------------------------
    shop_agg['SPI'] = (
        shop_agg['self_count'] - shop_agg['incorrect_self']
    ) / shop_agg['self_count']

    shop_agg['CPI'] = (
        shop_agg['comp_count'] - shop_agg['incorrect_comp']
    ) / shop_agg['comp_count']

    shop_agg['NPD'] = (
        shop_agg['others_count'] /
        (shop_agg['self_count'] +
         shop_agg['comp_count'] +
         shop_agg['others_count'])
    )

    shop_agg['total_count'] = (
        shop_agg['self_count'] +
        shop_agg['comp_count'] +
        shop_agg['others_count']
    )

    shop_agg['total_incorrect'] = (
        shop_agg['incorrect_self'] +
        shop_agg['incorrect_comp'] +
        shop_agg['incorrect_others']
    )

    shop_agg['accuracy'] = (
        shop_agg['total_count'] -
        shop_agg['total_incorrect']
    ) / shop_agg['total_count']

    print("Metrics calculated")

    # -----------------------------------------
    # AI Grade
    # -----------------------------------------
    F = shop_agg['accuracy']
    G = shop_agg['SPI']
    H = shop_agg['NPD']

    not_blank = (~F.isna()) & (~G.isna()) & (~H.isna())

    shop_agg['Ai_grade'] = ""

    shop_agg = assign_grade(shop_agg, F, G, H)
    
    print("AI grading completed")

    # -----------------------------------------
    # Final Columns removed recommendataion
    # -----------------------------------------
    final_cols_shop = [
        'category_id','category_name','capture_date','shop_id','total_image_count',
        'self_count','comp_count','others_count','sticker_count',
        'incorrect_self','incorrect_comp','incorrect_others',
        'SPI','CPI','NPD','total_count','total_incorrect','accuracy',
        'Ai_grade'
    ]

    shop_summary = shop_agg[final_cols_shop]
    # -----------------------------------------
    # Add Overall Row
    # -----------------------------------------
    overall_row = {
        'category_id': '',
        'category_name': 'Overall',
        'capture_date': '',
        'shop_id': '',
        'total_image_count': shop_summary['total_image_count'].sum(),
        'self_count': shop_summary['self_count'].sum(),
        'comp_count': shop_summary['comp_count'].sum(),
        'others_count': shop_summary['others_count'].sum(),
        'sticker_count': shop_summary['sticker_count'].sum(),
        'incorrect_self': shop_summary['incorrect_self'].sum(),
        'incorrect_comp': shop_summary['incorrect_comp'].sum(),
        'incorrect_others': shop_summary['incorrect_others'].sum(),
        'SPI': (shop_summary['self_count'].sum() - shop_summary['incorrect_self'].sum()) / shop_summary['self_count'].sum(),
        'CPI': (shop_summary['comp_count'].sum() - shop_summary['incorrect_comp'].sum()) / shop_summary['comp_count'].sum(),
        'NPD': shop_summary['others_count'].sum() / shop_summary['total_count'].sum(),
        'total_count': shop_summary['total_count'].sum(),
        'total_incorrect': shop_summary['total_incorrect'].sum(),
        'accuracy': (shop_summary['total_count'].sum() - shop_summary['total_incorrect'].sum()) / shop_summary['total_count'].sum(),
        'Ai_grade': ''  # will be assigned next
    }

    # Convert to DataFrame for grading
    overall_df = pd.DataFrame([overall_row])

    # Call assign_grade
    overall_df = assign_grade(
        overall_df,
        F=overall_df['accuracy'],
        G=overall_df['SPI'],
        H=overall_df['NPD']
    )

    # Append overall row to shop summary
    shop_summary = pd.concat([shop_summary, overall_df], ignore_index=True)

    # -----------------------------------------
    # Save CSV
    # -----------------------------------------
    shop_summary.to_csv(output_path, index=False)

    print("shopwise.csv created successfully")
    print("-" * 40)


# -----------------------------------------
# Entry Point
# -----------------------------------------
# if __name__ == "__main__":
#     run_shop_category(os.cwd())