import pandas as pd
import re

def apply_filters(df, query="", excluded="", states=None, min_price=0, max_price=0):
    if df.empty:
        return df.copy()
    out = df.copy()
    states = states or []
    if query.strip():
        terms = [t for t in re.split(r"\s+", query.strip().lower()) if t]
        haystack = out["title"].fillna("").astype(str).str.lower()
        # Mode A : recherche souple, au moins un des termes doit être présent.
        mask = haystack.apply(lambda value: any(term in value for term in terms))
        out = out[mask]
    if excluded.strip():
        terms = [t.strip().lower() for t in excluded.split(",") if t.strip()]
        haystack = out["title"].fillna("").astype(str).str.lower()
        for term in terms:
            out = out[~haystack.loc[out.index].str.contains(re.escape(term), na=False)]
    if states:
        out = out[out["condition"].fillna("").isin(states)]
    if min_price > 0:
        out = out[pd.to_numeric(out["price"], errors="coerce") >= min_price]
    if max_price > 0:
        out = out[pd.to_numeric(out["price"], errors="coerce") <= max_price]
    return out
