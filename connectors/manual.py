import streamlit as st
from datetime import date

def manual_listing_form():
    with st.form("manual_listing"):
        title = st.text_input("Titre de l'annonce")
        url = st.text_input("Lien de l'annonce")
        price = st.number_input("Prix (€)", min_value=0.0, step=1.0)
        condition = st.selectbox("État", ["", "Neuf avec étiquette", "Neuf sans étiquette", "Très bon état", "Bon état", "État satisfaisant"])
        shipping = st.number_input("Frais de livraison (€) — laisser 0 si inconnus", min_value=0.0, step=0.5)
        image_url = st.text_input("URL de la photo (facultatif)")
        published = st.date_input("Date de publication", value=date.today())
        submitted = st.form_submit_button("Ajouter")
    if submitted and title.strip():
        return {
            "listing_id": url.strip() or f"manual-{title.strip().lower().replace(' ', '-')}-{published.isoformat()}",
            "title": title.strip(), "url": url.strip() or None, "price": price,
            "condition": condition or None,
            "shipping_cost": shipping if shipping > 0 else None,
            "date_published": published.isoformat(),
            "image_url": image_url.strip() or None, "source": "manual"
        }
    return None
