import sqlite3

import streamlit as st

from conf import COORDINATES_COLUMNS
from load_data import load_assay_layout, load_qa_data
from plots import heatmap, histogram, box_plot_test_group
from sql_search import sql_save, sql_retrieve_above_threshold
from statistics import get_median_df

st.title('Image Validation App')
st.write('A viewer app for biologists to analyze the outputs of IMV (image validation).')

left_column, right_column = st.columns(2)
with left_column:
    qa_data = load_qa_data()
with right_column:
    assay_layout = load_assay_layout()

if qa_data is not None and assay_layout is not None:
    st.subheader('Analysis')
    features = [feature for feature in qa_data.columns if feature not in COORDINATES_COLUMNS]
    feature = st.selectbox('Select a feature:', features)
    qa_data_feature = qa_data[COORDINATES_COLUMNS + [feature]]

    st.altair_chart(histogram(qa_data_feature, feature))

    st.write('Choose wells for further analysis:')
    df_medians = get_median_df(assay_layout, qa_data, feature)
    test_group = heatmap(df_medians)

    if test_group is not None:
        st.altair_chart(box_plot_test_group(test_group, assay_layout, qa_data, feature))

    # SQL search
    if st.checkbox('SQL search'):
        db_conn = sqlite3.connect('db/file.db')

        sql_save(db_conn, assay_layout, qa_data, feature)

        threshold = st.slider(label='Variance threshold', min_value=0, max_value=99, step=5)
        retrieved_df_from_db = sql_retrieve_above_threshold(db_conn, threshold)
        retrieved_df_from_db
