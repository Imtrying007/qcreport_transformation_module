import os
import shutil
import uuid
import streamlit as st
from datetime import datetime, timedelta

# Base temp folder inside project directory
TMP_ROOT = os.path.join(os.getcwd(), "tmp_sessions")
os.makedirs(TMP_ROOT, exist_ok=True)


def init_run_session():
    """
    Create a new temporary run directory inside project folder.
    Deletes previous run if exists.
    """
    # Clean previous run
    if "run_dir" in st.session_state:
        try:
            shutil.rmtree(st.session_state["run_dir"])
        except Exception:
            pass

    # Create new temp directory inside tmp_sessions
    run_dir_name = f"qc_run_{uuid.uuid4().hex}"
    run_dir = os.path.join(TMP_ROOT, run_dir_name)
    os.makedirs(run_dir, exist_ok=True)

    st.session_state["run_dir"] = run_dir
    return run_dir


def get_run_dir():
    """
    Get current run directory
    """
    return st.session_state.get("run_dir", None)


def save_uploaded_file(uploaded_file, filename):
    """
    Save uploaded file inside run directory
    """
    run_dir = get_run_dir()
    if not run_dir:
        raise Exception("Run session not initialized")

    path = os.path.join(run_dir, filename)
    with open(path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return path


def cleanup_run(max_age_hours=0.25):
    """
    Delete the current session folder and optionally old session folders.
    Default max_age_hours=0.25 → 15 minutes
    """
    # Delete current session folder
    if "run_dir" in st.session_state:
        run_dir = st.session_state["run_dir"]
        if os.path.exists(run_dir):
            shutil.rmtree(run_dir)
        del st.session_state["run_dir"]

    # Delete old session folders in TMP_ROOT
    now = datetime.now()
    for folder in os.listdir(TMP_ROOT):
        folder_path = os.path.join(TMP_ROOT, folder)
        if os.path.isdir(folder_path):
            ctime = datetime.fromtimestamp(os.path.getctime(folder_path))
            if now - ctime > timedelta(hours=max_age_hours):
                try:
                    shutil.rmtree(folder_path)
                except Exception:
                    pass