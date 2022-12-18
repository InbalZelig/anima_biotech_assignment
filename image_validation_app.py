import pandas as pd
import streamlit as st

st.title('Image Validation App')
st.write('A viewer app for biologists to analyze the outputs of IMV (image validation).')


def load_assay_layout() -> pd.DataFrame:
    """
    Load Assay layout file and preprocess it:
    - Use only column 'Compound' and well coordinates.
    :return: df
    """
    uploaded_file = st.file_uploader("Choose an Assay Layout file")
    if uploaded_file is not None:
        assay_layout = pd.read_csv(uploaded_file)
        return assay_layout[['Row', 'Column', 'Compound']]


def load_qa_data() -> pd.DataFrame:
    """
    Load QA data file and preprocess it:
    - Remove last row.
    - Rename r, c, f to Row, Column, Field.
    - ignore 'message' column.
    :return: df
    """
    uploaded_file = st.file_uploader("Choose QA data file")
    if uploaded_file is not None:
        qa_data = pd.read_csv(uploaded_file)
        qa_data = qa_data[:-1]  # remove last row
        qa_data.drop(labels=['msg'], axis=1, inplace=True)
        qa_data.rename(columns={'r': 'Row', 'c': 'Column', 'f': 'Field'}, inplace=True)
        return qa_data


left_column, right_column = st.columns(2)
with left_column:
    qa_data = load_qa_data()
    if qa_data is not None:
        qa_data
with right_column:
    assay_layout = load_assay_layout()
    if assay_layout is not None:
        assay_layout
