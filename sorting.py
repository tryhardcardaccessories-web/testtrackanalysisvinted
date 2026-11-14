import pandas as pd

def sort_listings(df, column, ascending=True):
    if df.empty or column not in df.columns:
        return df
    out = df.copy()
    if column in ["price", "shipping_cost", "total_price"]:
        out[column] = pd.to_numeric(out[column], errors="coerce")
    elif column == "date_published":
        out[column] = pd.to_datetime(out[column], errors="coerce", utc=True)
    return out.sort_values(column, ascending=ascending, na_position="last", kind="stable")
