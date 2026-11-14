import pandas as pd

REQUIRED = {"listing_id", "title", "price"}

def parse_csv(file):
    df = pd.read_csv(file)
    missing = REQUIRED - set(df.columns)
    if missing:
        raise ValueError("Colonnes obligatoires manquantes : " + ", ".join(sorted(missing)))
    defaults = {
        "condition": None, "shipping_cost": None, "date_published": None,
        "url": None, "image_url": None, "source": "import_csv"
    }
    for col, value in defaults.items():
        if col not in df.columns:
            df[col] = value
    return df
