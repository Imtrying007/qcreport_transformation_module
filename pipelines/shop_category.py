import pandas as pd
import numpy as np
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utility.grading import assign_grade
from utility.recommendation import assign_recommendation
from utility.core_metrics import compute_core_metrics


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
    df = pd.read_csv(input_path)
    print("analytic.csv loaded successfully")

    # -----------------------------------------
    # Normalize
    # -----------------------------------------
    df['qc_class_name'] = df['qc_class_name'].astype(str).str.lower()
    df['qc_competition'] = df['qc_competition'].astype(str).str.lower()
    df['category_name'] = df['category_name'].astype(str)

    # -----------------------------------------
    # FLAGS
    # -----------------------------------------
    self_flag = df['qc_competition'] == 'self'
    comp_flag = df['qc_competition'] == 'competitor'

    raw_sticker_flag = df['qc_class_name'].str.contains('sticker', na=False)
    others_flag = df['qc_class_name'].str.contains('other', na=False)

    incorrect_flag = df['ai_correct'] == False

    # -----------------------------------------
    # STICKER LOGIC
    # -----------------------------------------
    exclude_sticker = raw_sticker_flag & df['ai_correct'].isna()

    # -----------------------------------------
    # PURE BUCKETS
    # -----------------------------------------
    pure_self = self_flag & ~others_flag & ~exclude_sticker
    pure_comp = comp_flag & ~others_flag & ~exclude_sticker

    # -----------------------------------------
    # OTHERS SPLIT
    # -----------------------------------------
    others_self = others_flag & self_flag
    others_comp = others_flag & comp_flag

    # -----------------------------------------
    # FLATTEN INTO DF (for reuse utility)
    # -----------------------------------------
    df['self_count'] = pure_self.astype(int)
    df['comp_count'] = pure_comp.astype(int)

    df['others_self'] = others_self.astype(int)
    df['others_comp'] = others_comp.astype(int)

    df['incorrect_self'] = (pure_self & incorrect_flag).astype(int)
    df['incorrect_comp'] = (pure_comp & incorrect_flag).astype(int)

    df['incorrect_others_self'] = (others_self & incorrect_flag).astype(int)
    df['incorrect_others_comp'] = (others_comp & incorrect_flag).astype(int)

    # -----------------------------------------
    # GROUPING
    # -----------------------------------------
    group_cols = ['category_id', 'category_name', 'shop_id', 'capture_date']

    shop_agg = df.groupby(group_cols).agg(
        total_image_count=('test_image_id', 'nunique'),

        self_count=('self_count', 'sum'),
        comp_count=('comp_count', 'sum'),

        others_self=('others_self', 'sum'),
        others_comp=('others_comp', 'sum'),

        sticker_count=('qc_class_name',
            lambda x: exclude_sticker.loc[x.index].sum()
        ),

        incorrect_self=('incorrect_self', 'sum'),
        incorrect_comp=('incorrect_comp', 'sum'),

        incorrect_others_self=('incorrect_others_self', 'sum'),
        incorrect_others_comp=('incorrect_others_comp', 'sum')
    ).reset_index()

    print("Shop-level aggregation completed")

    # -----------------------------------------
    # CORE METRICS (single source of truth)
    # -----------------------------------------
    shop_agg = compute_core_metrics(shop_agg)

    print("Metrics calculated via utility")

    # -----------------------------------------
    # GRADING
    # -----------------------------------------
    F = shop_agg['accuracy']
    G = shop_agg['SPI']
    H = shop_agg['NPD']

    shop_agg = assign_grade(shop_agg, F, G, H)
    print("AI grading completed")

    # -----------------------------------------
    # FINAL COLUMNS
    # -----------------------------------------
    final_cols = [
        'category_id', 'category_name', 'capture_date', 'shop_id',
        'total_image_count',
        'self_count', 'comp_count', 'others_self', 'others_comp',
        'sticker_count',
        'incorrect_self', 'incorrect_comp',
        'incorrect_others_self', 'incorrect_others_comp',
        'SPI', 'CPI', 'NPD',
        'total_count', 'total_incorrect', 'accuracy',
        'Ai_grade'
    ]

    shop_summary = shop_agg[final_cols]

    # -----------------------------------------
    # OVERALL ROW
    # -----------------------------------------
    total_df = pd.DataFrame([shop_summary.drop(
        columns=['category_id', 'category_name', 'shop_id', 'capture_date']
    ).sum(numeric_only=True)])

    total_df['category_id'] = ''
    total_df['category_name'] = 'OVERALL'
    total_df['shop_id'] = ''
    total_df['capture_date'] = ''

    total_df = compute_core_metrics(total_df)
    total_df = assign_grade(total_df, total_df['accuracy'], total_df['SPI'], total_df['NPD'])

    shop_summary = pd.concat([shop_summary, total_df], ignore_index=True)

    # -----------------------------------------
    # SAVE
    # -----------------------------------------
    shop_summary.to_csv(output_path, index=False)

    print("shopwise.csv created successfully")
    print("-" * 40)