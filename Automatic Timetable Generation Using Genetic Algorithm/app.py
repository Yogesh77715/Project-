import streamlit as st
import pandas as pd
import nbformat
import importlib.util
import os
from streamlit_extras.colored_header import colored_header
from streamlit_extras.add_vertical_space import add_vertical_space

# Convert backend.ipynb to backend.py
def convert_notebook_to_script(notebook_path, script_path):
    with open(notebook_path, "r", encoding="utf-8") as nb_file:
        notebook_content = nbformat.read(nb_file, as_version=4)

    script_content = ""
    for cell in notebook_content.cells:
        if cell.cell_type == "code":
            script_content += cell.source + "\n\n"

    with open(script_path, "w", encoding="utf-8") as py_file:
        py_file.write(script_content)

# Define paths
notebook_path = "backend.ipynb"
script_path = "backend.py"

# Convert notebook before importing
convert_notebook_to_script(notebook_path, script_path)

# Load backend.py dynamically
spec = importlib.util.spec_from_file_location("backend", script_path)
backend = importlib.util.module_from_spec(spec)
spec.loader.exec_module(backend)

# Import required functions from backend.py
load_excel_data = backend.load_excel_data
preprocess_course_data = backend.preprocess_course_data
genetic_algorithm = backend.genetic_algorithm
export_to_pdf = backend.export_to_pdf


st.set_page_config(page_title="AI Timetable Generator", layout="wide", page_icon="📅")

def main():
    colored_header(label="📅 AI Timetable Generator", description="Upload your data files to generate a conflict-free class timetable.", color_name="blue-70")
    add_vertical_space(1)

    with st.expander("ℹ️ How to Use"):
        st.markdown("""
        1. Upload all the required Excel files: **Course**, **Staff**, **Students**, and **Room** data.
        2. Click **Generate Timetable** to automatically create a conflict-free schedule.
        3. Download the generated timetable in PDF format.
        """)

    st.markdown("### 📂 Upload Your Files")
    col1, col2 = st.columns(2)
    with col1:
        course_file = st.file_uploader("📘 Upload Course Data", type=["xls", "xlsx"])
        students_file = st.file_uploader("🎓 Upload Students Data", type=["xls", "xlsx"])
    with col2:
        staff_file = st.file_uploader("🧑‍🏫 Upload Staff Data", type=["xls", "xlsx"])
        room_file = st.file_uploader("🏫 Upload Room Data", type=["xls", "xlsx"])

    add_vertical_space(1)
    if st.button("🚀 Generate Timetable"):
        if course_file and staff_file and students_file and room_file:
            with st.spinner("Generating optimized timetable, please wait..."):
                course_data = load_excel_data(course_file)
                staff_data = load_excel_data(staff_file)
                students_data = load_excel_data(students_file)
                room_data = load_excel_data(room_file)

                subjects, class_subject_staff, mca_classes, theory_rooms, lab_rooms = backend.process_data(course_data, students_data, room_data)

                timetable = genetic_algorithm(subjects, class_subject_staff, mca_classes, theory_rooms, lab_rooms)
                pdf_filename = export_to_pdf(timetable, class_subject_staff)

            st.success("✅ Timetable generated successfully!")
            with open(pdf_filename, "rb") as pdf_file:
                st.download_button(
                    label="📥 Download Timetable PDF",
                    data=pdf_file,
                    file_name="Timetable.pdf",
                    mime="application/pdf"
                )
        else:
            st.error("❗ Please upload all required files.")

if __name__ == "__main__":
    main()