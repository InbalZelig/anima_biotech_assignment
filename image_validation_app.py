from typing import Union

import pandas as pd
import streamlit as st

from conf import ROW_HEADER, COLUMN_HEADER, COMPOUND_HEADER, FIELD_HEADER, DMSO
from well import Well

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


def get_median_feature(qa_data: pd.DataFrame, feature: str, wells: Union[Well, list]) -> float:
    """
    Get the median of the given feature, taken over all data input that belong to the set of given wells
    (single or multiple wells).
    :param qa_data: df.
    :param feature: str. one of the headers in the given df.
    :param wells: a list of wells or a single well object.
    :return: median (float).
    """
    if type(wells) == list:
        filtered_df = pd.DataFrame()
        for well in wells:
            df_well = qa_data[(qa_data[ROW_HEADER] == well.row) & (qa_data[COLUMN_HEADER] == well.column)]
            filtered_df = pd.concat([filtered_df, df_well])
    else:
        filtered_df = qa_data[(qa_data[ROW_HEADER] == wells.row) & (qa_data[COLUMN_HEADER] == wells.column)]
    median = filtered_df[feature].median()
    return median


def get_dmso_median(assay_layout: pd.DataFrame, qa_data: pd.DataFrame, feature: str) -> float:
    """
    Get the median of the given feature over the walls annotated as 'DMSO'.
    :param assay_layout: df.
    :param qa_data: df.
    :param feature: str. one of the headers in the qa_data df.
    :return: median (float).
    """
    wells = get_dmso_wells(assay_layout)
    return get_median_feature(qa_data, feature, wells)


def get_dmso_wells(assay_layout: pd.DataFrame) -> [Well]:
    """
    Get a list of wells with 'DMSO'.
    :param assay_layout: df.
    :return: list of wells.
    """
    df_dmso = assay_layout[assay_layout[COMPOUND_HEADER] == DMSO]
    wells = []
    for _, row in df_dmso.iterrows():
        well = Well(row[ROW_HEADER], row[COLUMN_HEADER])
        wells.append(well)
    return wells


def variation_for_well_feature(assay_layout: pd.DataFrame, qa_data: pd.DataFrame, feature: str, well: Well) -> float:
    """
    Compute the feature variation of the given well & feature.
    The variation calculated as (well median)/(DMSO median) of the feature.
    :param assay_layout: df.
    :param qa_data: df.
    :param feature: str. one of the headers in the qa_data df.
    :param well: Well object.
    :return: variation (float).
    """
    dmso_median = get_dmso_median(assay_layout, qa_data, feature)
    if dmso_median != 0:
        well_median = get_median_feature(qa_data, feature, well)
        variation = well_median / dmso_median
        return variation
    else:
        st.error('DMSO median is zero! Can\'t calculate well variation.')


left_column, right_column = st.columns(2)
with left_column:
    qa_data = load_qa_data()

with right_column:
    assay_layout = load_assay_layout()

coordinates_columns = [ROW_HEADER, COLUMN_HEADER, FIELD_HEADER]

if qa_data is not None and assay_layout is not None:
    st.subheader('Analysis')
    features = [feature for feature in qa_data.columns if feature not in coordinates_columns]
    feature = st.selectbox('Select a feature:', features)
    qa_data_feature = qa_data[coordinates_columns + [feature]]

    st.write('Select well:')
    left_column, right_column = st.columns(2)
    with left_column:
        row_number = st.number_input('Insert row number', min_value=2, max_value=15, step=1)
    with right_column:
        column_number = st.number_input('Insert column number', min_value=2, max_value=23, step=1)

    well = Well(row_number, column_number)
    st.write('Selected compound:', well.get_compound_name(assay_layout))
    st.write('Well median:', get_median_feature(qa_data_feature, feature, well))
    st.write('DMSO median:', get_dmso_median(assay_layout, qa_data, feature))
    st.write('Well variation: (well median/DMSO median)',
             variation_for_well_feature(assay_layout, qa_data, feature, well))
