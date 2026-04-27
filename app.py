# app.py
import os
import streamlit as st
from utility.session_manager import init_run_session, save_uploaded_file, get_run_dir, cleanup_run

# Import pipeline functions (make sure they accept run_dir as argument)
from pipelines.main_file import run_main_file
from pipelines.image_level import run_image_level
from pipelines.shop_category import run_shop_category
from pipelines.summary import run_summary
from pipelines.notes import run_notes
from pipelines.excel_generation import run_excel_generation

# ----------------------------------------
# Page Config
# ----------------------------------------
st.set_page_config(
    page_title="QC Transformation Pipeline",
    page_icon="📊",
    layout="wide"
)

st.title("📊 QC Transformation Pipeline")
st.write("Upload QC Mode and CGC CSV files to run the pipeline. Each user session is isolated.")

# ----------------------------------------
# Initialize User Session
# ----------------------------------------
if "run_dir" not in st.session_state:
    run_dir = init_run_session()
    st.session_state["run_dir"] = run_dir
    st.success(f"Session started. Temporary workspace created: `{run_dir}`")
else:
    run_dir = st.session_state["run_dir"]
    st.info(f"Existing session workspace: `{run_dir}`")

st.write("Your session workspace directory:")
st.code(run_dir)

# ----------------------------------------
# Optional: Reset Session
# ----------------------------------------
if st.button("🧹 Reset Session"):
    cleanup_run()
    st.rerun()  # updated from experimental_rerun()

# ----------------------------------------
# File Upload
# ----------------------------------------
st.subheader("📂 Upload Files")

qc_mode_file = st.file_uploader("Upload QC Mode CSV File", type=["csv"])
cgc_file = st.file_uploader("Upload CGC CSV File", type=["csv"])

uploaded = False
if qc_mode_file:
    qc_path = save_uploaded_file(qc_mode_file, "qc_mode.csv")
    st.success(f"QC Mode CSV saved at `{qc_path}`")
    uploaded = True

if cgc_file:
    cgc_path = save_uploaded_file(cgc_file, "cgc.csv")
    st.success(f"CGC CSV saved at `{cgc_path}`")
    uploaded = True

if uploaded:
    st.info("Files are saved in your isolated session workspace. Ready to run the pipeline.")

# ----------------------------------------
# Run Pipeline
# ----------------------------------------
st.subheader("🚀 Run Pipeline")

if st.button("Run QC Transformation Pipeline"):

    run_dir = get_run_dir()  # user's session workspace

    try:
        st.info("Running main_file.py...")
        run_main_file(run_dir)
        st.success("Main pipeline completed ✅")

        st.info("Running image_level.py...")
        run_image_level(run_dir)
        st.success("Image level pipeline completed ✅")

        st.info("Running shop_category.py...")
        run_shop_category(run_dir)
        st.success("Shop-category pipeline completed ✅")

        st.info("Running summary.py...")
        run_summary(run_dir)
        st.success("Summary pipeline completed ✅")

        st.info("Running notes.py...")
        run_notes(run_dir)
        st.success("Notes pipeline completed ✅")

        st.info("Generating final Excel file...")
        excel_path = run_excel_generation(run_dir)
        st.success(f"Excel generated ✅ at `{excel_path}`")

        # Save output paths in session_state for downloads
        st.session_state['summary_path'] = os.path.join(run_dir, "summary.csv")
        st.session_state['notes_path'] = os.path.join(run_dir, "notes.csv")
        st.session_state['excel_path'] = excel_path

    except Exception as e:
        st.error(f"Pipeline execution failed ❌: {e}")

# ----------------------------------------
# Download Section
# ----------------------------------------
st.subheader("⬇️ Download Files")

if 'summary_path' in st.session_state and os.path.exists(st.session_state['summary_path']):
    with open(st.session_state['summary_path'], "rb") as f:
        st.download_button(
            label="Download summary.csv",
            data=f,
            file_name="summary.csv",
            mime="text/csv"
        )

if 'notes_path' in st.session_state and os.path.exists(st.session_state['notes_path']):
    with open(st.session_state['notes_path'], "rb") as f:
        st.download_button(
            label="Download notes.csv",
            data=f,
            file_name="notes.csv",
            mime="text/csv"
        )

if 'excel_path' in st.session_state and os.path.exists(st.session_state['excel_path']):
    with open(st.session_state['excel_path'], "rb") as f:
        st.download_button(
            label="Download final_output.xlsx",
            data=f,
            file_name="final_output.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

# ----------------------------------------
# Optional: Show current session files
# ----------------------------------------
st.subheader("📁 Files in Your Session")
if run_dir and os.path.exists(run_dir):
    for file in os.listdir(run_dir):
        st.write(file)