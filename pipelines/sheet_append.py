import pandas as pd


def run_sheet_append_pipeline(
    uploaded_files,
    remove_duplicates=True,
    excel_mode="Append All Sheets",
    selected_sheet=None
):

    all_dataframes = []

    # ----------------------------------------
    # Read Uploaded Files
    # ----------------------------------------
    for file in uploaded_files:

        filename = file.name.lower()

        # ----------------------------------------
        # CSV FILE
        # ----------------------------------------
        if filename.endswith(".csv"):

            df = pd.read_csv(file)

            all_dataframes.append(df)

        # ----------------------------------------
        # EXCEL FILE
        # ----------------------------------------
        elif filename.endswith(".xlsx"):

            # Append all sheets
            if excel_mode == "Append All Sheets":

                excel_sheets = pd.read_excel(
                    file,
                    sheet_name=None
                )

                for sheet_name, df in excel_sheets.items():

                    df["source_sheet"] = sheet_name

                    all_dataframes.append(df)

            # Append selected sheet
            elif excel_mode == "Select Specific Sheet":

                df = pd.read_excel(
                    file,
                    sheet_name=selected_sheet
                )

                df["source_sheet"] = selected_sheet

                all_dataframes.append(df)

    # ----------------------------------------
    # Handle Empty Upload
    # ----------------------------------------
    if not all_dataframes:

        return pd.DataFrame()

    # ----------------------------------------
    # Combine DataFrames
    # ----------------------------------------
    combined_df = pd.concat(
        all_dataframes,
        ignore_index=True
    )

    # ----------------------------------------
    # Remove Duplicates
    # ----------------------------------------
    if remove_duplicates:

        combined_df = combined_df.drop_duplicates()

    return combined_df