import sqlite3
from sqlite3 import Connection

import numpy as np
import pandas as pd
import streamlit as st

from conf import *
from statistics import get_variation_df


@st.cache(hash_funcs={Connection: id})
def get_connection(path: str = DB_FILE):
    return sqlite3.connect(path, check_same_thread=False)


@st.cache(hash_funcs={Connection: id})
def sql_save(db_conn, assay_layout, qa_data, feature) -> None:
    """
    Store the data uploaded by the user to a local SQLite database with two tables: data, assay.
    :param db_conn: sqlite3 connection object.
    :param assay_layout: df.
    :param qa_data: df.
    :param feature: str. one of the headers in the qa_data df.
    """
    sql_data_df = qa_data.select_dtypes(include=np.number)
    df_variation = get_variation_df(assay_layout, qa_data, feature)
    sql_data_df = pd.merge(sql_data_df, df_variation, how="left", on=[ROW_HEADER, COLUMN_HEADER])
    sql_data_df.to_sql(name='data', con=db_conn, if_exists='replace', index=False)
    assay_layout.to_sql(name='assay', con=db_conn, if_exists='replace', index=False)


@st.cache(hash_funcs={Connection: id})
def sql_retrieve_above_threshold(db_conn, threshold) -> pd.DataFrame:
    """
    Retrieve SQL query for variation above the given threshold.
    :param db_conn: sqlite3 connection object.
    :param threshold: int.
    :return: df.
    """
    return pd.read_sql(f'select * from data where {VARIATION_HEADER}>{threshold}', db_conn)
