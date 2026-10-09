"""Clean the raw marketing campaign data and engineer features.

Run:  python src/clean.py
Input : data/marketing_campaign_raw.csv
Output: data/marketing_campaign_clean.csv  and  a printed cleaning log
"""
import pandas as pd

RAW = "data/marketing_campaign_raw.csv"
CLEAN = "data/marketing_campaign_clean.csv"
REFERENCE_YEAR = 2014  # last customer joined in mid-2014, so ages are computed as of 2014

SPEND_COLS = ["MntWines", "MntFruits", "MntMeatProducts", "MntFishProducts",
              "MntSweetProducts", "MntGoldProds"]


def parse_join_date(s: pd.Series) -> pd.Series:
    """Dt_Customer is stored two ways:
    - 'dd-mm-yyyy' text (correct)
    - 'yyyy-mm-dd' dates that a spreadsheet auto-converted with day and month swapped.
    Fix both into one proper date column."""
    s = s.astype(str).str.slice(0, 10)
    is_dmy = s.str.match(r"^\d{2}-\d{2}-\d{4}$")
    out = pd.Series(pd.NaT, index=s.index, dtype="datetime64[ns]")
    out[is_dmy] = pd.to_datetime(s[is_dmy], format="%d-%m-%Y")
    swapped = pd.to_datetime(s[~is_dmy], format="%Y-%m-%d")
    out[~is_dmy] = [pd.Timestamp(year=d.year, month=d.day, day=d.month) for d in swapped]
    return out


def clean(raw: pd.DataFrame):
    log = []
    df = raw.copy()
    n0 = len(df)

    # 1. Dates
    df["Dt_Customer"] = parse_join_date(df["Dt_Customer"])
    log.append("Fixed mixed / day-month-swapped join dates (Dt_Customer)")

    # 2. Junk categories
    df["Marital_Status"] = df["Marital_Status"].replace({"Alone": "Single"})
    junk = df["Marital_Status"].isin(["Absurd", "YOLO"])
    log.append(f"Removed {junk.sum()} rows with invalid Marital_Status (Absurd / YOLO); merged 'Alone' into 'Single'")
    df = df[~junk]

    # 3. Impossible birth years
    bad_birth = df["Year_Birth"] < 1940
    log.append(f"Removed {bad_birth.sum()} rows with impossible birth year (< 1940)")
    df = df[~bad_birth]

    # 4. Income outlier
    out_inc = df["Income"] > 200_000
    log.append(f"Removed {out_inc.sum()} income outlier (> 200,000; the max is 666,666)")
    df = df[~out_inc]

    # 5. Missing income -> median of the same education group
    n_missing = df["Income"].isna().sum()
    df["Income"] = df["Income"].fillna(df.groupby("Education")["Income"].transform("median"))
    log.append(f"Filled {n_missing} missing Income values with the median of the same Education group")

    # 6. Constant columns carry no information
    df = df.drop(columns=["Z_CostContact", "Z_Revenue"])
    log.append("Dropped constant columns Z_CostContact and Z_Revenue")

    # 7. Feature engineering
    df["Age"] = REFERENCE_YEAR - df["Year_Birth"]
    df["Age_Group"] = pd.cut(df["Age"], [0, 34, 44, 54, 64, 120],
                             labels=["<35", "35-44", "45-54", "55-64", "65+"]).astype(str)
    df["Total_Spend"] = df[SPEND_COLS].sum(axis=1)
    df["Total_Purchases"] = df[["NumWebPurchases", "NumCatalogPurchases", "NumStorePurchases"]].sum(axis=1)
    df["Children"] = df["Kidhome"] + df["Teenhome"]
    df["Has_Children"] = (df["Children"] > 0).map({True: "Yes", False: "No"})
    df["Prev_Campaigns_Accepted"] = df[[f"AcceptedCmp{i}" for i in range(1, 6)]].sum(axis=1)
    df["Tenure_Days"] = (pd.Timestamp("2014-06-30") - df["Dt_Customer"]).dt.days
    df["Income_Group"] = pd.qcut(df["Income"], 4, labels=["Low", "Lower-Mid", "Upper-Mid", "High"]).astype(str)
    df["Recency_Band"] = pd.cut(df["Recency"], [-1, 24, 49, 74, 100],
                                labels=["0-24 days", "25-49 days", "50-74 days", "75-99 days"]).astype(str)
    df["Dt_Customer"] = df["Dt_Customer"].dt.strftime("%Y-%m-%d")
    log.append("Created: Age, Age_Group, Total_Spend, Total_Purchases, Children, Has_Children, "
               "Prev_Campaigns_Accepted, Tenure_Days, Income_Group, Recency_Band")

    log.append(f"Rows: {n0} -> {len(df)}")
    return df.reset_index(drop=True), log


if __name__ == "__main__":
    cleaned, steps = clean(pd.read_csv(RAW))
    cleaned.to_csv(CLEAN, index=False)
    print("\n".join(f"- {s}" for s in steps))
    print(f"\nSaved {CLEAN}  shape={cleaned.shape}")
