import pandas as pd
import streamlit as st

from conf import ROW_HEADER, COLUMN_HEADER, COMPOUND_HEADER, FIELD_HEADER

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


left_column, right_column = st.columns(2)
with left_column:
    qa_data = load_qa_data()

with right_column:
    assay_layout = load_assay_layout()

coordinates_columns = [ROW_HEADER, COLUMN_HEADER, FIELD_HEADER, COMPOUND_HEADER]

if qa_data is not None and assay_layout is not None:
    st.subheader('Analysis')
    qa_data = pd.merge(qa_data, assay_layout, how="left", on=[ROW_HEADER, COLUMN_HEADER])
    features = [feature for feature in qa_data.columns if feature not in coordinates_columns]
    feature = st.selectbox('Select a feature:', features)
    qa_data_feature = qa_data[coordinates_columns + [feature]]
    qa_data_feature
