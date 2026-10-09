
"""Marketing Campaign Response Dashboard (Streamlit).
Run:  streamlit run app.py
"""
import re
import sqlite3

import pandas as pd
import plotly.express as px
import streamlit as st

CLEAN_CSV = "marketing_campaign_clean.csv"
QUERY_FILE = "queries.sql"


def load_queries(path: str = QUERY_FILE) -> dict:
    """Parse queries.sql into {name: {'question': ..., 'sql': ...}}."""
    text = open(path, encoding="utf-8").read()
    queries = {}
    for block in re.split(r"(?m)^-- name:\s*", text)[1:]:
        name, _, rest = block.partition("\n")
        m = re.match(r"-- question:\s*(.*)\n", rest)
        question = m.group(1).strip() if m else ""
        sql = rest[m.end():] if m else rest
        queries[name.strip()] = {"question": question, "sql": sql.strip()}
    return queries


st.set_page_config(page_title="Marketing Campaign Analysis", page_icon="📈", layout="wide")


@st.cache_data
def load_data() -> pd.DataFrame:
    return pd.read_csv(CLEAN_CSV)


def run_query(sql: str) -> pd.DataFrame:
    """Run SQL on an in-memory SQLite database built from the clean CSV."""
    with sqlite3.connect(":memory:") as con:
        load_data().to_sql("customers", con, index=False)
        return pd.read_sql_query(sql, con)


df = load_data()

DIMENSIONS = {
    "Income group": "Income_Group",
    "Number of children": "Children",
    "Days since last purchase": "Recency_Band",
    "Earlier campaigns accepted": "Prev_Campaigns_Accepted",
    "Education": "Education",
    "Marital status": "Marital_Status",
    "Age group": "Age_Group",
}
ORDERS = {
    "Income_Group": ["Low", "Lower-Mid", "Upper-Mid", "High"],
    "Recency_Band": ["0-24 days", "25-49 days", "50-74 days", "75-99 days"],
    "Age_Group": ["<35", "35-44", "45-54", "55-64", "65+"],
}

st.title("📈 Marketing Campaign Response Analysis")
st.caption("Which customers accept a marketing campaign, and how should we target them? "
           "Data: 2,232 customers of a food & wine retailer (Kaggle: Customer Personality Analysis), after cleaning.")

# ---------------- Sidebar filters ----------------
with st.sidebar:
    st.header("Filters")
    edu = st.multiselect("Education", sorted(df["Education"].unique()), default=sorted(df["Education"].unique()))
    mar = st.multiselect("Marital status", sorted(df["Marital_Status"].unique()),
                         default=sorted(df["Marital_Status"].unique()))
    inc_lo, inc_hi = int(df["Income"].min()), int(df["Income"].max())
    inc = st.slider("Income", inc_lo, inc_hi, (inc_lo, inc_hi), step=1000)
    age = st.slider("Age", int(df["Age"].min()), int(df["Age"].max()),
                    (int(df["Age"].min()), int(df["Age"].max())))

view = df[df["Education"].isin(edu) & df["Marital_Status"].isin(mar)
          & df["Income"].between(*inc) & df["Age"].between(*age)]
if view.empty:
    st.warning("No customers match these filters.")
    st.stop()

overall_rate = df["Response"].mean() * 100
rate = view["Response"].mean() * 100

k1, k2, k3, k4 = st.columns(4)
k1.metric("Customers", f"{len(view):,}")
k2.metric("Response rate", f"{rate:.1f}%", f"{rate - overall_rate:+.1f} pts vs all customers")
k3.metric("Avg total spend", f"{view['Total_Spend'].mean():,.0f}")
k4.metric("Avg income", f"{view['Income'].mean():,.0f}")

tab1, tab2, tab3, tab4 = st.tabs(["Who responds?", "Spend & channels", "Build a target profile", "SQL queries"])

# ---------------- Tab 1 ----------------
with tab1:
    label = st.selectbox("Break down response rate by", list(DIMENSIONS))
    col = DIMENSIONS[label]
    g = view.groupby(col).agg(Customers=("Response", "size"), Response_rate=("Response", "mean")).reset_index()
    g["Response_rate"] = (g["Response_rate"] * 100).round(1)
    if col in ORDERS:
        g[col] = pd.Categorical(g[col], ORDERS[col], ordered=True)
    g = g.sort_values(col)
    g[col] = g[col].astype(str)
    fig = px.bar(g, x=col, y="Response_rate", text="Response_rate", hover_data=["Customers"],
                 labels={"Response_rate": "Response rate (%)", col: label})
    fig.add_hline(y=overall_rate, line_dash="dash", line_color="orange",
                  annotation_text=f"All customers: {overall_rate:.1f}%")
    fig.update_traces(texttemplate="%{text}%", marker_color="#2F5D9E")
    st.plotly_chart(fig)
    st.caption("Small groups (see Customers on hover) can look extreme by chance. "
               "These are patterns in past data, not proof of cause.")

# ---------------- Tab 2 ----------------
with tab2:
    a, b = st.columns(2)
    with a:
        st.subheader("Spend by product category")
        cats = {"Wines": "MntWines", "Meat": "MntMeatProducts", "Gold": "MntGoldProds",
                "Fish": "MntFishProducts", "Sweets": "MntSweetProducts", "Fruits": "MntFruits"}
        cat = pd.DataFrame({"Category": list(cats), "Spend": [view[c].sum() for c in cats.values()]})
        st.plotly_chart(px.pie(cat, names="Category", values="Spend", hole=0.45))
    with b:
        st.subheader("Purchases per customer by channel")
        ch = view.assign(Type=view["Response"].map({1: "Responder", 0: "Non-responder"})).groupby("Type").agg(
            Web=("NumWebPurchases", "mean"), Catalog=("NumCatalogPurchases", "mean"),
            Store=("NumStorePurchases", "mean")).reset_index().melt("Type", var_name="Channel", value_name="Avg purchases")
        st.plotly_chart(px.bar(ch, x="Channel", y="Avg purchases", color="Type", barmode="group"))
    st.subheader("Responders vs non-responders")
    cmp_ = view.assign(Type=view["Response"].map({1: "Responder", 0: "Non-responder"})).groupby("Type").agg(
        Customers=("Response", "size"), Avg_income=("Income", "mean"), Avg_total_spend=("Total_Spend", "mean"),
        Avg_wine_spend=("MntWines", "mean"), Avg_meat_spend=("MntMeatProducts", "mean")).round(0).reset_index()
    st.dataframe(cmp_, hide_index=True)

# ---------------- Tab 3 ----------------
with tab3:
    st.write("Pick a customer profile and compare its response rate with everyone else.")
    p1, p2, p3 = st.columns(3)
    inc_groups = p1.multiselect("Income group", ORDERS["Income_Group"], default=["High"])
    max_kids = p2.slider("Max children", 0, 3, 0)
    max_rec = p3.slider("Max days since last purchase", 0, 99, 49)
    mask = df["Income_Group"].isin(inc_groups) & (df["Children"] <= max_kids) & (df["Recency"] <= max_rec)
    if mask.sum() == 0:
        st.warning("No customers match this profile.")
    else:
        t, r = df[mask], df[~mask]
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Customers in profile", f"{len(t):,}", f"{len(t) / len(df) * 100:.1f}% of all")
        m2.metric("Profile response rate", f"{t['Response'].mean() * 100:.1f}%")
        m3.metric("Everyone else", f"{r['Response'].mean() * 100:.1f}%" if len(r) else "n/a")
        m4.metric("Avg spend (profile)", f"{t['Total_Spend'].mean():,.0f}")
        st.caption("Tip: High income + 0 children + 49 days is the profile used in SQL query 13. "
                   "It was chosen after exploring this same data, so treat it as a hypothesis to test "
                   "in the next campaign, not a guaranteed result.")

# ---------------- Tab 4 ----------------
with tab4:
    st.write("All analysis questions are answered with SQL on a SQLite database. Pick a query to see the code and result.")
    queries = load_queries()
    name = st.selectbox("Query", list(queries))
    st.markdown(f"**Question:** {queries[name]['question']}")
    st.code(queries[name]["sql"], language="sql")
    st.dataframe(run_query(queries[name]["sql"]), hide_index=True)