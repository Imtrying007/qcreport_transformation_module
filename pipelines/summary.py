import pandas as pd
import numpy as np
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utility.grading import assign_grade
from utility.recommendation import assign_recommendation
from utility.core_metrics import compute_core_metrics


def run_summary(run_dir):

    print("Starting Summary Pipeline...")
    print("-" * 40)

    input_path = os.path.join(run_dir, "analytic.csv")
    output_path = os.path.join(run_dir, "summary.csv")

    # -----------------------------------------
    # LOAD DATA
    # -----------------------------------------
    df = pd.read_csv(input_path)

    # -----------------------------------------
    # NORMALIZE
    # -----------------------------------------
    df['qc_class_name'] = df['qc_class_name'].astype(str).str.lower()
    df['qc_competition'] = df['qc_competition'].astype(str).str.lower()

    # -----------------------------------------
    # FLAGS
    # -----------------------------------------
    self_flag = df['qc_competition'] == 'self'
    comp_flag = df['qc_competition'] == 'competitor'

    others_flag = df['qc_class_name'].str.contains('other', na=False)
    raw_sticker_flag = df['qc_class_name'].str.contains('sticker', na=False)

    incorrect_flag = df['ai_correct'] == False

    # -----------------------------------------
    # STICKER LOGIC
    # -----------------------------------------
    exclude_sticker = raw_sticker_flag & df['ai_correct'].isna()
    sticker_flag = exclude_sticker

    # -----------------------------------------
    # PURE BUCKETS
    # -----------------------------------------
    pure_self = self_flag & ~others_flag & ~exclude_sticker
    pure_comp = comp_flag & ~others_flag & ~exclude_sticker

    # -----------------------------------------
    # OTHERS SPLIT
    # -----------------------------------------
    others_self_flag = others_flag & self_flag
    others_comp_flag = others_flag & comp_flag

    # -----------------------------------------
    # INJECT FEATURES FOR GROUPBY
    # -----------------------------------------
    df['self_count'] = pure_self.astype(int)
    df['comp_count'] = pure_comp.astype(int)

    df['others_self'] = others_self_flag.astype(int)
    df['others_comp'] = others_comp_flag.astype(int)

    df['incorrect_self'] = (pure_self & incorrect_flag).astype(int)
    df['incorrect_comp'] = (pure_comp & incorrect_flag).astype(int)

    df['incorrect_others_self'] = (others_self_flag & incorrect_flag).astype(int)
    df['incorrect_others_comp'] = (others_comp_flag & incorrect_flag).astype(int)

    # -----------------------------------------
    # GROUPING
    # -----------------------------------------
    group_cols = ['category_id', 'category_name']

    cat_agg = df.groupby(group_cols).agg(

        total_image_count=('test_image_id', 'nunique'),

        self_count=('self_count', 'sum'),
        comp_count=('comp_count', 'sum'),

        others_self=('others_self', 'sum'),
        others_comp=('others_comp', 'sum'),

        sticker_count=('qc_class_name',
            lambda x: sticker_flag.loc[x.index].sum()
        ),

        incorrect_self=('incorrect_self', 'sum'),
        incorrect_comp=('incorrect_comp', 'sum'),

        incorrect_others_self=('incorrect_others_self', 'sum'),
        incorrect_others_comp=('incorrect_others_comp', 'sum'),

    ).reset_index()

    print("Aggregation completed")

    # -----------------------------------------
    # DERIVED FIELDS
    # -----------------------------------------
    cat_agg['others_count'] = (
        cat_agg['others_self'] + cat_agg['others_comp']
    )

    cat_agg['incorrect_others'] = (
        cat_agg['incorrect_others_self'] +
        cat_agg['incorrect_others_comp']
    )

    cat_agg['total_count'] = (
        cat_agg['self_count'] +
        cat_agg['comp_count'] +
        cat_agg['others_count']
    )

    cat_agg['total_incorrect'] = (
        cat_agg['incorrect_self'] +
        cat_agg['incorrect_comp'] +
        cat_agg['incorrect_others']
    )

    # -----------------------------------------
    # CORE METRICS
    # -----------------------------------------
    cat_agg = compute_core_metrics(cat_agg)

    print("Metrics computed")

    # -----------------------------------------
    # GRADE + RECOMMENDATION
    # -----------------------------------------
    cat_agg = assign_grade(
        cat_agg,
        cat_agg['accuracy'],
        cat_agg['SPI'],
        cat_agg['NPD']
    )

    cat_agg = assign_recommendation(
        cat_agg,
        cat_agg['accuracy'],
        cat_agg['SPI'],
        cat_agg['NPD']
    )

    print("Grading completed")

    # -----------------------------------------
    # OVERALL ROW
    # -----------------------------------------
    overall = cat_agg.drop(
        columns=['category_id', 'category_name']
    ).sum(numeric_only=True).to_dict()

    overall['category_id'] = ""
    overall['category_name'] = "OVERALL"

    overall = pd.DataFrame([overall])

    overall = compute_core_metrics(overall)

    overall = assign_grade(
        overall,
        overall['accuracy'],
        overall['SPI'],
        overall['NPD']
    )

    overall = assign_recommendation(
        overall,
        overall['accuracy'],
        overall['SPI'],
        overall['NPD']
    )

    cat_agg = pd.concat([cat_agg, overall], ignore_index=True)

    # -----------------------------------------
    # FINAL COLUMN ORDER (STRICT)
    # -----------------------------------------
    cat_agg = cat_agg[
        [
            'category_id', 'category_name', 'total_image_count',
            'self_count', 'comp_count', 'others_count',
            'sticker_count',
            'incorrect_self', 'incorrect_comp', 'incorrect_others',
            'SPI', 'CPI', 'NPD',
            'total_count', 'total_incorrect', 'accuracy',
            'Ai_grade', 'recommendation'
        ]
    ]

    # -----------------------------------------
    # SAVE
    # -----------------------------------------
    cat_agg.to_csv(output_path, index=False)

    print("summary.csv created successfully")
    print("-" * 40)