# recommendation.py

import pandas as pd

def assign_recommendation(df, F, G, H):
    df['recommendation'] = ""

    not_blank = (~F.isna()) & (~G.isna()) & (~H.isna())

    # F > 0.95
    cond1 = not_blank & (F > 0.95)

    # H < 0.1
    cond1a = cond1 & (H < 0.1)

    df.loc[cond1a & (G > 0.95),
           'recommendation'] = "Sturdy category, no recommendations"

    df.loc[cond1a & (G <= 0.95),
           'recommendation'] = "Hard category! Needs active interference and addition of groups for the client. Lot of new packshots might have been introduced in the market. Either that or data science team needs to build a specialized pipeline."

    # 0.1 <= H < 0.3
    cond1b = cond1 & (H >= 0.1) & (H < 0.3)

    df.loc[cond1b & (G > 0.95),
           'recommendation'] = "Category is okay for now, however, recommend adding new products to make sure it is future proof."

    df.loc[cond1b & (G <= 0.95),
           'recommendation'] = "Too many products need to be added as groups. This category doesn’t seem to have regular addition of groups and needs active interference."

    # H >= 0.3
    cond1c = cond1 & (H >= 0.3)

    df.loc[cond1c & (G > 0.95),
           'recommendation'] = "Category is okay for now. But too many products are not added yet. This would cause issues with new products being launched."

    df.loc[cond1c & (G <= 0.95),
           'recommendation'] = "Looks like a totally ignored category with not enough groups added, recommend immediate escalation."

    # F <= 0.95
    cond2 = not_blank & (F <= 0.95)

    # G > 0.95
    cond2a = cond2 & (G > 0.95)

    df.loc[cond2a & (H < 0.1),
           'recommendation'] = "Looks like a competitor SKU dataset has some issue or it is a GT category, in which case it is okay."

    df.loc[cond2a & (H >= 0.1),
           'recommendation'] = "Either a GT category, in which case it should work. If an MT category, immediate attention needs to be paid to competitors and others dataset."

    # G <= 0.95
    cond2b = cond2 & (G <= 0.95)

    df.loc[cond2b & (H < 0.3),
           'recommendation'] = "Either a hard GT category where expectations should be set well or a category that data science team should look into with high priority. Can be due to similar looking SKUs or dataset creation errors."

    df.loc[cond2b & (H >= 0.3),
           'recommendation'] = "This category should not have gone to production or is being ignored for a long time depending upon how long it has been around. Immediate escalation recommended"

    return df