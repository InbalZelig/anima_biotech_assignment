import altair as alt
import pandas as pd
import streamlit as st
from streamlit_vega_lite import altair_component

from conf import COLUMN_HEADER, ROW_HEADER, MEDIAN_HEADER, DMSO, VARIATION_HEADER
from statistics import variation_for_well_feature
from well import Well


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


def histogram(df: pd.DataFrame, feature: str):
    return alt.Chart(df).mark_bar().encode(
        alt.X(f"{feature}:Q", bin=True),
        y="count()"
    ).properties(
        title=f'Histogram for: {feature}'
    )


def box_plot_test_group(test_group: pd.DataFrame, assay_layout: pd.DataFrame, qa_data: pd.DataFrame, feature: str):
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
    return box_plot
