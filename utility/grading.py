# grading.py
import pandas as pd
import numpy as np

def assign_grade(df, F, G, H):
    """
    Assign AI grades based on accuracy (F), SPI (G), and NPD (H).
    Fully vectorized using numpy.select for efficiency.
    """

    # Define conditions
    not_blank = (~F.isna()) & (~G.isna()) & (~H.isna())

    conditions = [
        not_blank & (F > 0.95) & (H < 0.1) & (G > 0.95),
        not_blank & (F > 0.95) & (H < 0.1) & (G <= 0.95),
        not_blank & (F > 0.95) & (H >= 0.1) & (H < 0.3) & (G > 0.95),
        not_blank & (F > 0.95) & (H >= 0.1) & (H < 0.3) & (G <= 0.95),
        not_blank & (F > 0.95) & (H >= 0.3) & (G > 0.95),
        not_blank & (F > 0.95) & (H >= 0.3) & (G <= 0.95),
        not_blank & (F <= 0.95) & (G > 0.95) & (H < 0.1),
        not_blank & (F <= 0.95) & (G > 0.95) & (H >= 0.1),
        not_blank & (F <= 0.95) & (G <= 0.95) & (H < 0.3),
        not_blank & (F <= 0.95) & (G <= 0.95) & (H >= 0.3)
    ]

    # Corresponding grades
    choices = ["A", "D", "B", "E", "C", "F", "B", "C", "D", "F"]

    # Assign grades
    df['Ai_grade'] = np.select(conditions, choices, default="")

    return df