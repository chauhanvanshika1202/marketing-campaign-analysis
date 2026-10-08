import pandas as pd
import plotly.express as px
import streamlit as st

# Title and Overview
st.title("Marketing Campaign Response & Customer Segmentation")
st.write(
    "Analyzing 2,232 customer records to optimize marketing campaign performance."
)

# Sample Data Metric Display
col1, col2, col3 = st.columns(3)
col1.metric("Total Customers", "2,232")
col2.metric("Overall Response Rate", "14.9%")
col3.metric("High-Income Segment Response", "45.3%")

# Key Finding Visualization Note
st.subheader("Key Segment Insight")
st.write(
    "Customers with high income and zero children show a significantly higher response rate (45.3%) compared to the average baseline."
)
