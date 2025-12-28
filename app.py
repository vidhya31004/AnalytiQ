import streamlit as st
import pandas as pd
import plotly.express as px
from groq import Groq
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from io import BytesIO
import os

st.set_page_config(page_title="AnalytiQ", layout="wide")

st.title("📊 AnalytiQ – AI-Powered Analytics Dashboard")

# Groq client
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Upload
uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

if uploaded_file is None:
    st.info("👆 Upload a CSV file to begin analysis")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    # Preview
    st.subheader("📄 Data Preview")
    st.dataframe(df.head())

    # Summary
    st.subheader("📊 Summary Statistics")
    st.write(df.describe())

    # Columns
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    categorical_cols = df.select_dtypes(include="object").columns.tolist()

    # Charts
    st.subheader("📈 Visual Analytics")

    if numeric_cols:
        metric = st.selectbox("Select numeric metric", numeric_cols)

        if categorical_cols:
            category = st.selectbox("Group by category", categorical_cols)
            plot_df = df.groupby(category)[metric].mean().reset_index()
            fig = px.bar(
                plot_df,
                x=category,
                y=metric,
                title=f"{metric} by {category}"
            )
        else:
            fig = px.histogram(
                df,
                x=metric,
                title=f"Distribution of {metric}"
            )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No numeric columns available.")

    # AI Section
    st.subheader("🤖 Ask AI About Your Data")

    ai_question = st.text_area(
        "Ask about insights, risks, trends, or actions"
    )

    if ai_question:
        with st.spinner("Analyzing with AI..."):
            context = f"""
            Dataset shape: {df.shape}

            Summary statistics:
            {df.describe().to_string()}
            """

            response = groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a senior business analyst. "
                            "Respond with sections:\n"
                            "Key Insights\n"
                            "Risks / Anomalies\n"
                            "Recommended Actions"
                        )
                    },
                    {"role": "user", "content": context},
                    {"role": "user", "content": ai_question}
                ],
                temperature=0.3,
                max_tokens=500
            )

            ai_answer = response.choices[0].message.content
            st.session_state["ai_answer"] = ai_answer

            st.success("AI Insights")
            st.write(ai_answer)

    # PDF Export
    st.subheader("📄 Download Executive Report")

    if "ai_answer" in st.session_state:
        if st.button("Download PDF Report"):
            buffer = BytesIO()
            pdf = canvas.Canvas(buffer, pagesize=A4)
            width, height = A4
            y = height - 50

            pdf.setFont("Helvetica-Bold", 16)
            pdf.drawString(50, y, "AnalytiQ – Executive AI Report")

            y -= 40
            pdf.setFont("Helvetica", 11)
            pdf.drawString(
                50, y,
                f"Rows: {df.shape[0]} | Columns: {df.shape[1]}"
            )

            y -= 30
            pdf.setFont("Helvetica", 10)

            for line in st.session_state["ai_answer"].split("\n"):
                if y < 50:
                    pdf.showPage()
                    pdf.setFont("Helvetica", 10)
                    y = height - 50
                pdf.drawString(50, y, line)
                y -= 14

            pdf.save()
            buffer.seek(0)

            st.download_button(
                "📥 Download PDF",
                buffer,
                file_name="AnalytiQ_Report.pdf",
                mime="application/pdf"
            )

