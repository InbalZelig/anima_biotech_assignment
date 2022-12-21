import sqlite3
from typing import Union

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st
from streamlit_vega_lite import altair_component

from conf import *
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


def variation_for_well_feature(assay_layout: pd.DataFrame, qa_data: pd.DataFrame, feature: str,
                               wells: Union[Well, list]) -> float:
    """
    Compute the feature variation of the given well & feature.
    The variation calculated as (well median)/(DMSO median) of the feature.
    :param assay_layout: df.
    :param qa_data: df.
    :param feature: str. one of the headers in the qa_data df.
    :param wells: a list of wells or a single well object.
    :return: variation (float).
    """
    dmso_median = get_dmso_median(assay_layout, qa_data, feature)
    if dmso_median != 0:
        well_median = get_median_feature(qa_data, feature, wells)
        variation = well_median / dmso_median
        return variation
    else:
        st.error('DMSO median is zero! Can\'t calculate well variation.')


def get_median_df(assay_layout: pd.DataFrame, qa_data: pd.DataFrame, feature: str) -> pd.DataFrame:
    """
    Create a dataFrame to work with feature's median in all the wells.
    :param assay_layout: df.
    :param qa_data: df.
    :param feature: str. one of the headers in the qa_data df.
    :return: median df.
    """
    df_medians = pd.DataFrame()
    for _, assay_layout_row in assay_layout.iterrows():
        well = Well(assay_layout_row[ROW_HEADER], assay_layout_row[COLUMN_HEADER])
        median = get_median_feature(qa_data, feature, well)
        tmp_df = pd.DataFrame({ROW_HEADER: [well.row], COLUMN_HEADER: [well.column], MEDIAN_HEADER: [median]})
        df_medians = pd.concat([df_medians, tmp_df], ignore_index=True)
    return df_medians


def get_variation_df(assay_layout: pd.DataFrame, qa_data: pd.DataFrame, feature: str) -> pd.DataFrame:
    """
    Create a dataFrame to work with feature's median in all the wells.
    :param assay_layout: df.
    :param qa_data: df.
    :param feature: str. one of the headers in the qa_data df.
    :return: median df.
    """
    df_variation = pd.DataFrame()
    for _, assay_layout_row in assay_layout.iterrows():
        well = Well(assay_layout_row[ROW_HEADER], assay_layout_row[COLUMN_HEADER])
        variation = variation_for_well_feature(assay_layout, qa_data, feature, well)
        tmp_df = pd.DataFrame({ROW_HEADER: [well.row], COLUMN_HEADER: [well.column], VARIATION_HEADER: [variation]})
        df_variation = pd.concat([df_variation, tmp_df], ignore_index=True)
    return df_variation


def heatmap(df_medians: pd.DataFrame) -> pd.DataFrame:
    """
    Create 2D heatmap of selected feature median values.
    The heatmap enable brushing of a set of wells.
    :param df_medians: df.
    :return: filtered median df based on the brushing.
    """

    @st.cache
    def altair_heatmap():
        selector = alt.selection_interval()
        return (
            alt.Chart(df_medians).mark_rect().encode(
                x=f'{COLUMN_HEADER}:O',
                y=f'{ROW_HEADER}:O',
                color=alt.condition(selector, f'{MEDIAN_HEADER}:Q', alt.value('lightgray'))
            ).add_selection(
                selector
            ).properties(
                title=f'Median Heatmap of the plate'
            )
        )

    event_dict = altair_component(altair_chart=altair_heatmap())

    col_bounds, row_bounds = event_dict.get(COLUMN_HEADER), event_dict.get(ROW_HEADER)
    if col_bounds:
        col_min, col_max = min(col_bounds), max(col_bounds)
        row_min, row_max = min(row_bounds), max(row_bounds)
        test_group = df_medians[
            (df_medians[COLUMN_HEADER] >= col_min)
            & (df_medians[COLUMN_HEADER] <= col_max)
            & (df_medians[ROW_HEADER] >= row_min)
            & (df_medians[ROW_HEADER] <= row_max)
            ]
        return test_group


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

    histogram_chart = alt.Chart(qa_data).mark_bar().encode(
        alt.X(f"{feature}:Q", bin=True),
        y="count()"
    ).properties(
        title=f'Histogram for: {feature}'
    )

    st.altair_chart(histogram_chart)

    st.write('Choose wells for further analysis:')
    df_medians = get_median_df(assay_layout, qa_data, feature)
    test_group = heatmap(df_medians)

    if test_group is not None:
        wells = []
        for _, row in test_group.iterrows():
            well = Well(row[ROW_HEADER], row[COLUMN_HEADER])
            wells.append(well)

        test_group_variation = variation_for_well_feature(assay_layout, qa_data, feature, wells)

        box_plot_df = pd.DataFrame({'group': [DMSO, 'test-group'], VARIATION_HEADER: [1, test_group_variation]})
        box_plot = alt.Chart(box_plot_df).mark_bar().encode(
            x='group:O',
            y=f"{VARIATION_HEADER}:Q"
        ).properties(
            title=f'Selected wells variation',
            width=400
        )

        st.altair_chart(box_plot)

    # SQL search
    db_conn = sqlite3.connect('file.db')

    sql_data_df = qa_data.select_dtypes(include=np.number)
    df_variation = get_variation_df(assay_layout, qa_data, feature)
    sql_data_df = pd.merge(sql_data_df, df_variation, how="left", on=[ROW_HEADER, COLUMN_HEADER])
    sql_data_df.to_sql(name='data', con=db_conn, if_exists='replace', index=False)

    assay_layout.to_sql(name='assay', con=db_conn, if_exists='replace', index=False)

    threshold = st.slider(label='Variance threshold', min_value=0, max_value=99, step=5)

    retrieved_df_from_db = pd.read_sql(f'select * from data where {VARIATION_HEADER}>{threshold}', db_conn)
    retrieved_df_from_db
