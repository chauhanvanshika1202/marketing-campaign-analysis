import pandas as pd

# Load dataset
df = pd.read_csv("marketing_campaign.csv", sep="\t")

# 1. Data Cleaning: Handle Missing Values
# Filling missing income values with the median income
df["Income"] = df["Income"].fillna(df["Income"].median())

# 2. Feature Engineering: Total Spending across all product categories
df["Total_Spent"] = (
    df["MntWines"]
    + df["MntFruits"]
    + df["MntMeatProducts"]
    + df["MntFishProducts"]
    + df["MntSweetProducts"]
    + df["MntGoldProds"]
)

# 3. Feature Engineering: Total Children in Household
df["Total_Children"] = df["Kidhome"] + df["Teenhome"]

# 4. Customer Segmentation based on Income and Children
def segment_customer(row):
    if row["Income"] > 70000 and row["Total_Children"] == 0:
        return "High Income, No Kids"
    elif row["Income"] > 70000 and row["Total_Children"] > 0:
        return "High Income, With Kids"
    else:
        return "Other Segments"

df["Customer_Segment"] = df.apply(segment_customer, axis=1)

# Summary of Segment Response Rate
segment_analysis = df.groupby("Customer_Segment")["Response"].mean() * 100
print(segment_analysis)
