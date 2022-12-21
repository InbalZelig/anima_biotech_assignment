import pandas as pd
import streamlit as st

from conf import ROW_HEADER, COLUMN_HEADER, COMPOUND_HEADER, FIELD_HEADER


def load_assay_layout() -> pd.DataFrame:
    """
    Load Assay layout file and preprocess it:
    - Use only column 'Compound' and well coordinates.
    :return: df
    """
    uploaded_file = st.file_uploader("Choose an Assay Layout file")
    if uploaded_file is not None:
        assay_layout = pd.read_csv(uploaded_file)
        return assay_layout[[ROW_HEADER, COLUMN_HEADER, COMPOUND_HEADER]]


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
        qa_data.rename(columns={'r': ROW_HEADER, 'c': COLUMN_HEADER, 'f': FIELD_HEADER}, inplace=True)
        return qa_data
