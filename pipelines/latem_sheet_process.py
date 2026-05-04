import pandas as pd

REQUIRED_COLUMNS = {
    "image_status",
    "category_name",
    "annotated_image_link",
    "image_capture_timestamp"
}


def load_file(uploaded_file):
    if uploaded_file.name.endswith(".csv"):
        return pd.read_csv(uploaded_file)
    elif uploaded_file.name.endswith(".xlsx"):
        return pd.read_excel(uploaded_file)
    else:
        raise ValueError("Unsupported file format")


def validate_columns(df):
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {missing}")


def apply_quota_with_date_fallback(df, quota):

    if quota == 0:
        return df

    result = []

    for category, group in df.groupby("category_name"):

        date_groups = {
            d: g.copy()
            for d, g in group.groupby("Capture Date")
        }

        total = sum(len(g) for g in date_groups.values())

        if total <= quota:
            result.append(group)
            continue

        alloc = {
            d: int((len(g) / total) * quota)
            for d, g in date_groups.items()
        }

        for d in alloc:
            alloc[d] = min(alloc[d], len(date_groups[d]))

        remaining = quota - sum(alloc.values())

        while remaining > 0:
            candidates = [
                d for d in date_groups
                if alloc[d] < len(date_groups[d])
            ]

            if not candidates:
                break

            d = max(candidates, key=lambda x: len(date_groups[x]) - alloc[x])
            alloc[d] += 1
            remaining -= 1

        for d, g in date_groups.items():
            result.append(g.head(alloc[d]))

    return pd.concat(result, ignore_index=True)


# ==============================
# MAIN PIPELINE FUNCTION
# ==============================
def run_latem_sheet_process(uploaded_file, entries_per_shop, max_entries_per_category):

    try:
        # STEP 1: Load file
        df = load_file(uploaded_file)
        validate_columns(df)

        # STEP 2: Filter valid images
        df_valid = df[
            df["image_status"].astype(str).str.lower() == "valid"
        ].copy()

        if df_valid.empty:
            return None, "No valid images found"

        # STEP 3: Date parsing
        df_valid["Capture Date"] = pd.to_datetime(
            df_valid["image_capture_timestamp"],
            errors="coerce"
        ).dt.date

        df_valid = df_valid.dropna(subset=["Capture Date"])

        # STEP 4: quota logic
        if max_entries_per_category > 0:
            df_valid = apply_quota_with_date_fallback(
                df_valid,
                max_entries_per_category
            )

        # STEP 5: cleanup
        df_valid = df_valid.rename(
            columns={"category_name": "Category Name"}
        )

        df_valid["Image Link"] = (
            df_valid["annotated_image_link"]
            .fillna("")
            .str.replace(
                "https://view.shelfwatch.io/?url=",
                "",
                regex=False
            )
        )

        df_valid = df_valid[
            ["Category Name", "Image Link", "Capture Date"]
        ]

        # STEP 6: SHOP batching
        shop_frames = []

        for (cat, date), group in df_valid.groupby(["Category Name", "Capture Date"]):

            group = group.reset_index(drop=True)

            num_shops = (len(group) + entries_per_shop - 1) // entries_per_shop

            for i in range(num_shops):

                start = i * entries_per_shop
                end = start + entries_per_shop

                chunk = group.iloc[start:end].copy()

                chunk["SHOP ID"] = f"QC_T_{cat}_{date}_S_{i+1}"

                shop_frames.append(chunk)

        df_final = pd.concat(shop_frames, ignore_index=True)

        processed_df = df_final[
            ["SHOP ID", "Category Name", "Image Link"]
        ]

        # summary
        summary_df = (
            df_final.groupby(["Category Name", "Capture Date"])
            .size()
            .reset_index(name="Selected Count")
        )

        category_total = (
            df_final.groupby("Category Name")
            .size()
            .reset_index(name="Total Selected")
        )

        summary_df = summary_df.merge(category_total, on="Category Name")

        return {
            "processed": processed_df,
            "summary": summary_df,
            "raw": df_final
        }, None

    except Exception as e:
        return None, str(e)