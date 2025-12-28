import streamlit as st
import pandas as pd
import plotly.express as px

st.title("AI Data Dashboard – AnalytiQ")

uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    st.subheader("📄 Data Preview")
    st.dataframe(df.head())

    st.success("DEBUG: Data loaded successfully")

    # -------- BASIC STATS --------
    st.subheader("📊 Summary Statistics")
    st.write(df.describe())

    # -------- SIMPLE CHART --------
    numeric_cols = df.select_dtypes(include="number").columns

    st.write("Numeric columns detected:", list(numeric_cols))

    if len(numeric_cols) > 0:
        col = st.selectbox("Select a numeric column", numeric_cols)
        fig = px.histogram(df, x=col)
        st.plotly_chart(fig)
    else:
        st.warning("No numeric columns found to plot.")

    st.success("DEBUG: Reached end of app")

