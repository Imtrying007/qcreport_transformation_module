# app.py

import os
import streamlit as st

from utility.session_manager import (
    init_run_session,
    save_uploaded_file,
    get_run_dir,
    cleanup_run
)

# ---------------- Pipeline Imports ----------------
from pipelines.main_file import run_main_file
from pipelines.image_level import run_image_level
from pipelines.shop_category import run_shop_category
from pipelines.summary import run_summary
from pipelines.notes import run_notes
from pipelines.excel_generation import run_excel_generation
from pipelines.latem_sheet_process import run_latem_sheet_process


# ----------------------------------------
# Page Configuration
# ----------------------------------------
st.set_page_config(
    page_title="QC Transformation Pipeline",
    page_icon="📊",
    layout="wide"
)

# ----------------------------------------
# Sidebar Navigation (MAIN ROUTER)
# ----------------------------------------
page = st.sidebar.radio(
    "Select Feature",
    ["QC Pipeline", "Latem Sheet Processor"]
)

# ========================================
# PAGE 1: QC PIPELINE
# ========================================
if page == "QC Pipeline":

    st.title("📊 QC Transformation Pipeline")
    st.write("Upload QC Mode and CGC CSV files to run the pipeline.")

    # ----------------------------------------
    # Initialize User Session (isolated workspace)
    # ----------------------------------------
    if "run_dir" not in st.session_state:
        run_dir = init_run_session()
        st.session_state["run_dir"] = run_dir
        st.success(f"Session started: `{run_dir}`")
    else:
        run_dir = st.session_state["run_dir"]
        st.info(f"Using existing session: `{run_dir}`")

    st.code(run_dir)

    # ----------------------------------------
    # Reset Session (safe cleanup)
    # ----------------------------------------
    if st.button("🧹 Reset Session"):
        cleanup_run()
        st.session_state.clear()   # IMPORTANT: clears stale state
        st.rerun()

    # ----------------------------------------
    # File Upload Section
    # ----------------------------------------
    st.subheader("📂 Upload Files")

    qc_mode_file = st.file_uploader(
        "Upload QC Mode CSV",
        type=["csv"],
        key="qc_file"
    )

    cgc_file = st.file_uploader(
        "Upload CGC CSV",
        type=["csv"],
        key="cgc_file"
    )

    uploaded = False

    if qc_mode_file:
        qc_path = save_uploaded_file(qc_mode_file, "qc_mode.csv")
        st.success(f"QC Mode saved: `{qc_path}`")
        uploaded = True

    if cgc_file:
        cgc_path = save_uploaded_file(cgc_file, "cgc.csv")
        st.success(f"CGC saved: `{cgc_path}`")
        uploaded = True

    if uploaded:
        st.info("Files uploaded. Ready to run pipeline.")

    # ----------------------------------------
    # Run Pipeline
    # ----------------------------------------
    st.subheader("🚀 Run Pipeline")

    if st.button("Run QC Transformation Pipeline"):

        run_dir = get_run_dir()

        try:
            st.info("Running main_file...")
            run_main_file(run_dir)
            st.success("Main completed ✅")

            st.info("Running image_level...")
            run_image_level(run_dir)
            st.success("Image level completed ✅")

            st.info("Running shop_category...")
            run_shop_category(run_dir)
            st.success("Shop-category completed ✅")

            st.info("Running summary...")
            run_summary(run_dir)
            st.success("Summary completed ✅")

            st.info("Running notes...")
            run_notes(run_dir)
            st.success("Notes completed ✅")

            st.info("Generating Excel...")
            excel_path = run_excel_generation(run_dir)
            st.success(f"Excel generated: `{excel_path}`")

            # Save paths in session for downloads
            st.session_state['summary_path'] = os.path.join(run_dir, "summary.csv")
            st.session_state['notes_path'] = os.path.join(run_dir, "notes.csv")
            st.session_state['excel_path'] = excel_path

        except Exception as e:
            st.error(f"Pipeline failed ❌: {e}")

    # ----------------------------------------
    # Download Section
    # ----------------------------------------
    st.subheader("⬇️ Download Files")

    if 'summary_path' in st.session_state and os.path.exists(st.session_state['summary_path']):
        with open(st.session_state['summary_path'], "rb") as f:
            st.download_button(
                "Download summary.csv",
                f,
                "summary.csv"
            )

    if 'notes_path' in st.session_state and os.path.exists(st.session_state['notes_path']):
        with open(st.session_state['notes_path'], "rb") as f:
            st.download_button(
                "Download notes.csv",
                f,
                "notes.csv"
            )

    if 'excel_path' in st.session_state and os.path.exists(st.session_state['excel_path']):
        with open(st.session_state['excel_path'], "rb") as f:
            st.download_button(
                "Download final_output.xlsx",
                f,
                "final_output.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    # ----------------------------------------
    # Show Files in Session Directory
    # ----------------------------------------
    st.subheader("📁 Session Files")

    if run_dir and os.path.exists(run_dir):
        for file in os.listdir(run_dir):
            st.write(file)


# ========================================
# PAGE 2: LATAM SHEET PROCESSOR
# ========================================
elif page == "Latem Sheet Processor":

    st.title("CSV / Excel Image Processor")

    # ----------------------------------------
    # Sidebar (scoped ONLY to this page)
    # ----------------------------------------
    with st.sidebar:
        st.header("Processing Settings")

        entries_per_shop = st.number_input(
            "Entries per SHOP ID",
            min_value=1,
            max_value=1000,
            value=20
        )

        max_entries_per_category = st.number_input(
            "Max entries per category (0 = no limit)",
            min_value=0,
            max_value=100000,
            value=1
        )

    # ----------------------------------------
    # File Upload
    # ----------------------------------------
    uploaded_file = st.file_uploader(
        "Upload CSV or Excel",
        type=["csv", "xlsx"],
        key="latem_file"
    )

    if not uploaded_file:
        st.info("Please upload a CSV or Excel file to begin.")
    else:
        # ----------------------------------------
        # Processing
        # ----------------------------------------
        with st.spinner("Processing..."):
            result, error = run_latem_sheet_process(
                    uploaded_file,
                    entries_per_shop,
                    max_entries_per_category
                )

        if error:
            st.warning(error)
        else:
            st.success("Processing complete ✅")

            # Preview
            st.subheader("Preview")

            # Category summary
            st.subheader("Category Summary")
            if error:
                st.warning(error)
            else:
                st.success("Processing complete ✅")

                processed_df = result["processed"]
                summary_df = result["summary"]

                # Preview
                st.subheader("Preview")
                st.dataframe(processed_df.head(50))

                # Summary
                st.subheader("Category Summary")
                st.dataframe(summary_df)

                # Download
                csv_data = processed_df.to_csv(index=False).encode("utf-8")

                st.download_button(
                    "Download shop CSV",
                    csv_data,
                    "processed_output.csv",
                    mime="text/csv"
                )
                csv_data2 = summary_df.to_csv(index=False).encode("utf-8")

                st.download_button(
                    "Download Date summary CSV",
                    csv_data2,
                    "cat_date_summary_.csv",
                    mime="text/csv"
                )
