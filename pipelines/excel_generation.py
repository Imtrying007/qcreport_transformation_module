import os
import pandas as pd


# ----------------------------------------
# Excel Generation
# ----------------------------------------
def run_excel_generation(run_dir):

    print("Starting Excel Generation...")
    print("-" * 40)

    shop_path = os.path.join(run_dir, "shopwise.csv")
    image_path = os.path.join(run_dir, "image_wise.csv")
    summary_path = os.path.join(run_dir, "summary.csv")
    notes_path = os.path.join(run_dir, "notes.csv")
    analytic_path = os.path.join(run_dir, "analytic.csv")

    output_excel = os.path.join(run_dir, "final_output.xlsx")

    files_added = 0

    with pd.ExcelWriter(output_excel, engine="openpyxl") as writer:

        # ----------------------------------------
        # Analytic Sheet
        # ----------------------------------------
        if os.path.exists(analytic_path):
            analytic_df = pd.read_csv(analytic_path)
            analytic_df.to_excel(writer, sheet_name="analytic", index=False)
            print("analytic.csv added to Excel")
            files_added += 1
        else:
            print("analytic.csv not found")

        # ----------------------------------------
        # Shopwise Sheet
        # ----------------------------------------
        if os.path.exists(shop_path):
            shop_df = pd.read_csv(shop_path)
            shop_df.to_excel(writer, sheet_name="shopwise", index=False)
            print("shopwise.csv added to Excel")
            files_added += 1
        else:
            print("shopwise.csv not found")

        # ----------------------------------------
        # Image Wise Sheet
        # ----------------------------------------
        if os.path.exists(image_path):
            image_df = pd.read_csv(image_path)
            image_df.to_excel(writer, sheet_name="image_wise", index=False)
            print("image_wise.csv added to Excel")
            files_added += 1
        else:
            print("image_wise.csv not found")

        # ----------------------------------------
        # Summary Sheet
        # ----------------------------------------
        if os.path.exists(summary_path):
            summary_df = pd.read_csv(summary_path)
            summary_df.to_excel(writer, sheet_name="summary", index=False)
            print("summary.csv added to Excel")
            files_added += 1
        else:
            print("summary.csv not found")

        # ----------------------------------------
        # Notes Sheet
        # ----------------------------------------
        if os.path.exists(notes_path):
            notes_df = pd.read_csv(notes_path)
            notes_df.to_excel(writer, sheet_name="notes", index=False)
            print("notes.csv added to Excel")
            files_added += 1
        else:
            print("notes.csv not found")

    # ----------------------------------------
    # Final Status
    # ----------------------------------------
    if files_added == 0:
        print("No CSV files found. Excel not created.")
        return None
    else:
        print("-" * 40)
        print("final_output.xlsx created in data folder")
        return output_excel


# ----------------------------------------
# Entry Point
# ----------------------------------------
if __name__ == "__main__":
    run_excel_generation()