import pandas as pd

REQUIRED_COLUMNS = {
    "image_status",
    "category_name",
    "annotated_image_link"
}

OPTIONAL_TIMESTAMP_COLUMNS = {
    "image_capture_timestamp",
    "tool_timestamp"
}

# ==============================
# VALIDATION
# ==============================
def validate_columns(df):
    missing_required = REQUIRED_COLUMNS - set(df.columns)

    if missing_required:
        raise ValueError(f"Missing required columns: {missing_required}")

    if not (
        "image_capture_timestamp" in df.columns
        or "tool_timestamp" in df.columns
    ):
        raise ValueError(
            "Missing timestamp columns: need at least one of "
            "'image_capture_timestamp' or 'tool_timestamp'"
        )

# ==============================
# FILE LOADER
# ==============================
def load_file(uploaded_file):
    if uploaded_file.name.endswith(".csv"):
        return pd.read_csv(uploaded_file)
    elif uploaded_file.name.endswith(".xlsx"):
        return pd.read_excel(uploaded_file)
    else:
        raise ValueError("Unsupported file format")

# ==============================
# QUOTA LOGIC
# ==============================
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
# MAIN PIPELINE
# ==============================
def run_latem_sheet_process(uploaded_file, entries_per_shop, max_entries_per_category):

    try:
        # STEP 1: Load
        df = load_file(uploaded_file)
        validate_columns(df)

        # STEP 2: filter valid images
        df_valid = df[
            df["image_status"].astype(str).str.lower() == "valid"
        ].copy()

        if df_valid.empty:
            return None, "No valid images found"

        # ==============================
        # STEP 3: SAFE TIMESTAMP HANDLING
        # ==============================

        ts1 = (
            df_valid["image_capture_timestamp"]
            if "image_capture_timestamp" in df_valid.columns
            else pd.Series(pd.NA, index=df_valid.index, dtype="string")
        )

        ts2 = (
            df_valid["tool_timestamp"]
            if "tool_timestamp" in df_valid.columns
            else pd.Series(pd.NA, index=df_valid.index, dtype="string")
        )

        df_valid["raw_timestamp"] = (
            ts1.fillna(ts2)
            .astype("string")
        )

        df_valid["Capture Date"] = pd.to_datetime(
            df_valid["raw_timestamp"],
            errors="coerce"
        )

        invalid_count = df_valid["Capture Date"].isna().sum()

        if invalid_count > 0:
            print(f"Invalid timestamps removed: {invalid_count}")

        df_valid = df_valid.dropna(subset=["Capture Date"])

        # normalize date (stable grouping)
        df_valid["Capture Date"] = df_valid["Capture Date"].dt.date

        if df_valid.empty:
            return None, "No valid timestamps after processing"

        full_valid_df = df_valid.copy()

        # STEP 4: quota
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

        if df_valid.empty:
            return None, "No data after filtering"

        # STEP 6: SHOP batching
        shop_frames = []

        for (cat, date), group in df_valid.groupby(
            ["Category Name", "Capture Date"]
        ):

            group = group.reset_index(drop=True)

            num_shops = (
                len(group) + entries_per_shop - 1
            ) // entries_per_shop

            safe_cat = str(cat).replace(" ", "_").replace("/", "_")

            for i in range(num_shops):

                start = i * entries_per_shop
                end = start + entries_per_shop

                chunk = group.iloc[start:end].copy()

                chunk["SHOP ID"] = f"QC_T_{safe_cat}_{date}_S_{i+1}"

                shop_frames.append(chunk)

        if not shop_frames:
            return None, "No SHOP frames generated"

        df_final = pd.concat(shop_frames, ignore_index=True)

        processed_df = df_final[
            ["SHOP ID", "Category Name", "Image Link"]
        ]

        # ==============================
        # LEFTOVER DATA
        # ==============================

        # keep original valid dataframe untouched
        original_valid_df = df[
            df["image_status"].astype(str).str.lower() == "valid"
        ].copy()

        # normalize processed links
        processed_links = set(
            processed_df["Image Link"]
            .fillna("")
            .astype(str)
            .str.strip()
            .str.rstrip("/")
            .str.lower()
        )

        # normalize original links
        normalized_links = (
            original_valid_df["annotated_image_link"]
            .fillna("")
            .astype(str)
            .str.replace(
                "https://view.shelfwatch.io/?url=",
                "",
                regex=False
            )
            .str.strip()
            .str.rstrip("/")
            .str.lower()
        )

        # keep only unprocessed rows
        left_df_next_cycle = original_valid_df[
            ~normalized_links.isin(processed_links)
        ].copy()

        # ==============================
        # SUMMARY
        # ==============================
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
            "raw": df_final,
            "left_for_next_cycle": left_df_next_cycle
        }, None

    except Exception as e:
        return None, str(e)