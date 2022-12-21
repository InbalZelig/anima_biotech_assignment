from typing import Union

import pandas as pd
import streamlit as st

from conf import ROW_HEADER, COLUMN_HEADER, COMPOUND_HEADER, DMSO, MEDIAN_HEADER, VARIATION_HEADER
from well import Well


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
