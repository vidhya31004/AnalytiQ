import streamlit as st
import pandas as pd

st.title("AI Data Dashboard – Day 1")

uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.write("Here are the first 5 rows:")
    st.dataframe(df.head())

