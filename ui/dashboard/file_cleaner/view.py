import streamlit as st
import os
import subprocess

from ui.dashboard.file_cleaner.file_cleaner import (
    scan_files,
    analyze_files,
    get_safe_files,
    delete_files,
    format_size,
    FOLDERS_TO_SCAN
)

# from features.cleaner.file_cleaner import *


# -----------------------------
# Open File Function
# -----------------------------
def open_file(path):
    try:
        os.startfile(path)  # Windows
    except:
        subprocess.Popen(["xdg-open", path])  # Linux fallback


# -----------------------------
# Main UI Function
# -----------------------------
def render_file_cleaner():
    st.header("🧹 Smart File Cleaner")

    # -----------------------------
    # Scan Button
    # -----------------------------
    if st.button("🔍 Scan System"):
        with st.spinner("Scanning files... Please wait..."):
            files = scan_files(FOLDERS_TO_SCAN)
            analyzed = analyze_files(files)
            safe_files, total_size = get_safe_files(analyzed)

            st.session_state["safe_files"] = safe_files
            st.session_state["total_size"] = total_size

            st.success("Scan Completed!")

    # -----------------------------
    # Show Results
    # -----------------------------
    if "safe_files" in st.session_state:
        st.subheader("🟢 Safe to Delete Files")

        st.write(f"Total Files: {len(st.session_state['safe_files'])}")
        st.write(f"Space You Can Free: {format_size(st.session_state['total_size'])}")

        # -----------------------------
        # AI Advice
        # -----------------------------
        if st.session_state["total_size"] > 1 * 1024 * 1024 * 1024:
            st.warning("⚠️ Large junk detected. Cleaning recommended!")
        else:
            st.info("✅ Your system looks clean.")

        st.divider()

        # -----------------------------
        # File List with Actions
        # -----------------------------
        for i, f in enumerate(st.session_state["safe_files"][:20]):
            col1, col2, col3 = st.columns([6, 1, 1])

            with col1:
                st.write(f"{f['path']} ({format_size(f['size'])})")

            with col2:
                if st.button("👁️", key=f"view_{i}"):
                    open_file(f["path"])

            with col3:
                if st.button("🗑️", key=f"delete_{i}"):
                    st.session_state["delete_target"] = f

        # -----------------------------
        # Individual Delete Confirmation
        # -----------------------------
        if "delete_target" in st.session_state:
            file_to_delete = st.session_state["delete_target"]

            st.warning(f"⚠️ Are you sure you want to delete?\n\n{file_to_delete['path']}")

            col1, col2 = st.columns(2)

            with col1:
                if st.button("✅ Yes Delete", key="confirm_delete"):
                    try:
                        os.remove(file_to_delete["path"])
                        st.success("File deleted successfully!")

                        # Remove from UI list
                        st.session_state["safe_files"] = [
                            f for f in st.session_state["safe_files"]
                            if f["path"] != file_to_delete["path"]
                        ]

                    except:
                        st.error("Failed to delete file!")

                    del st.session_state["delete_target"]

            with col2:
                if st.button("❌ Cancel", key="cancel_delete"):
                    del st.session_state["delete_target"]

        st.divider()

        # -----------------------------
        # Bulk Delete (Safe)
        # -----------------------------
        if st.button("🗑️ Clean All Safe Files"):
            st.session_state["confirm_bulk_delete"] = True

        if "confirm_bulk_delete" in st.session_state:
            st.warning("⚠️ Delete ALL safe files?")

            col1, col2 = st.columns(2)

            with col1:
                if st.button("✅ Yes, Delete All", key="bulk_yes"):
                    deleted, failed = delete_files(st.session_state["safe_files"])

                    st.success(f"Deleted: {deleted} files")
                    if failed > 0:
                        st.error(f"Failed: {failed} files")

                    # Clear UI list
                    st.session_state["safe_files"] = []

                    del st.session_state["confirm_bulk_delete"]

            with col2:
                if st.button("❌ Cancel", key="bulk_cancel"):
                    del st.session_state["confirm_bulk_delete"]