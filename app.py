import streamlit as st
import pandas as pd
from datetime import datetime
from database import init_db, save_search, list_searches, delete_search, upsert_listings, get_listings, mark_seen, get_seen_ids
from filters import apply_filters
from sorting import sort_listings
from connectors.csv_import import parse_csv
from connectors.manual import manual_listing_form
from connectors.vinted import search_vinted

st.set_page_config(page_title="Vinted Tracker", page_icon="🔎", layout="wide")
init_db()

st.title("🔎 Vinted Tracker")
st.caption("Moteur de recherche multi-sources — les résultats dépendent des sources de données connectées.")

with st.sidebar:
    st.header("Recherche")
    query = st.text_input("Mots-clés", placeholder="Ex. miniature Warhammer Teclis")
    excluded = st.text_input("Mots à exclure (séparés par des virgules)", placeholder="Ex. notice, boîte vide")
    states = st.multiselect(
        "État",
        ["Neuf avec étiquette", "Neuf sans étiquette", "Très bon état", "Bon état", "État satisfaisant"],
        default=[]
    )
    min_price = st.number_input("Prix minimum (€)", min_value=0.0, value=0.0, step=1.0)
    max_price = st.number_input("Prix maximum (€)", min_value=0.0, value=0.0, step=5.0,
                                help="0 = aucun maximum")
    only_unseen = st.checkbox("Masquer les annonces déjà vues", value=False)
    search_button = st.button("Rechercher sur Vinted", type="primary", use_container_width=True)

tabs = st.tabs(["Résultats", "Importer des annonces", "Recherches surveillées", "À propos"])

if search_button and query.strip():
    with st.spinner("Recherche en cours sur Vinted..."):
        live_items = search_vinted(query)
        if live_items:
            upsert_listings(live_items)
            st.success(f"{len(live_items)} annonces récupérées et enregistrées.")
            st.rerun()
        else:
            st.warning("Aucune annonce trouvée ou accès restreint par Vinted.")

with tabs[0]:
    all_rows = get_listings()
    df = pd.DataFrame(all_rows)
    if df.empty:
        st.info("Aucune annonce dans la base pour le moment. Lance une recherche ou importe un CSV.")
    else:
        filtered = apply_filters(
            df,
            query=query,
            excluded=excluded,
            states=states,
            min_price=min_price,
            max_price=max_price
        )
        if only_unseen:
            seen = get_seen_ids()
            filtered = filtered[~filtered["listing_id"].isin(seen)]

        st.subheader("Annonces")
        st.caption(f"{len(filtered)} résultat(s) dans la base")
        if not filtered.empty:
            c1, c2, c3 = st.columns([2, 1, 1])
            sort_col = c1.selectbox(
                "Trier par colonne",
                ["date_published", "price", "shipping_cost", "total_price", "condition", "title"],
                format_func=lambda x: {
                    "date_published": "Date de publication",
                    "price": "Prix",
                    "shipping_cost": "Frais de livraison",
                    "total_price": "Prix total",
                    "condition": "État",
                    "title": "Titre"
                }[x]
            )
            direction = c2.radio("Ordre", ["Décroissant", "Croissant"], horizontal=True)
            page_size = c3.selectbox("Annonces par page", [10, 25, 50, 100], index=1)
            filtered = sort_listings(filtered, sort_col, ascending=(direction == "Croissant"))
            page_count = max(1, (len(filtered) + page_size - 1) // page_size)
            page = st.number_input("Page", min_value=1, max_value=page_count, value=1, step=1)
            start = (page - 1) * page_size
            page_df = filtered.iloc[start:start + page_size].copy()

            display_cols = ["title", "price", "condition", "shipping_cost", "total_price", "date_published", "source"]
            display = page_df[display_cols].rename(columns={
                "title": "Annonce", "price": "Prix (€)", "condition": "État",
                "shipping_cost": "Envoi (€)", "total_price": "Total (€)",
                "date_published": "Date", "source": "Source"
            })
            st.dataframe(display, use_container_width=True, hide_index=True)

            st.markdown("#### Liens et détails")
            for _, row in page_df.iterrows():
                with st.container(border=True):
                    cols = st.columns([1, 5, 1])
                    if row.get("image_url"):
                        cols[0].image(row["image_url"], use_container_width=True)
                    else:
                        cols[0].markdown("🖼️")
                    cols[1].markdown(f"**{row['title']}**")
                    cols[1].write(
                        f"Prix : {row['price']:.2f} € · État : {row.get('condition') or 'Non renseigné'} · "
                        f"Livraison : {row['shipping_cost'] if pd.notna(row['shipping_cost']) else 'Indisponible'}"
                    )
                    cols[1].caption(f"Total estimé : {row['total_price'] if pd.notna(row['total_price']) else 'Indisponible'} € · {row.get('date_published') or ''}")
                    if row.get("url"):
                        cols[2].link_button("Ouvrir", row["url"])
                    if st.button("Marquer comme vue", key=f"seen_{row['listing_id']}"):
                        mark_seen(row["listing_id"])
                        st.rerun()
        else:
            st.warning("Aucune annonce ne correspond aux filtres.")

with tabs[1]:
    st.subheader("Ajouter des annonces")
    uploaded = st.file_uploader("Importer un CSV", type=["csv"])
    if uploaded:
        try:
            imported = parse_csv(uploaded)
            st.dataframe(imported.head(20), use_container_width=True)
            if st.button("Enregistrer les annonces importées", type="primary"):
                count = upsert_listings(imported.to_dict("records"))
                st.success(f"{count} annonce(s) importée(s) ou mise(s) à jour.")
                st.rerun()
        except Exception as exc:
            st.error(f"CSV invalide : {exc}")

    st.divider()
    st.subheader("Ajouter une annonce manuellement")
    manual = manual_listing_form()
    if manual:
        upsert_listings([manual])
        st.success("Annonce ajoutée.")
        st.rerun()

with tabs[2]:
    st.subheader("Recherches surveillées")
    with st.form("save_search_form"):
        s_name = st.text_input("Nom de la recherche", value=query or "")
        s_query = st.text_input("Mots-clés", value=query)
        s_excluded = st.text_input("Mots à exclure", value=excluded)
        s_states = st.multiselect("États acceptés", ["Neuf avec étiquette", "Neuf sans étiquette", "Très bon état", "Bon état", "État satisfaisant"], default=states)
        s_min = st.number_input("Prix minimum", min_value=0.0, value=float(min_price))
        s_max = st.number_input("Prix maximum (0 = aucun)", min_value=0.0, value=float(max_price))
        submitted = st.form_submit_button("Surveiller cette recherche")
        if submitted and s_query.strip():
            save_search(s_name or s_query, s_query, s_excluded, s_states, s_min, s_max)
            st.success("Recherche enregistrée.")
    searches = list_searches()
    if searches:
        for item in searches:
            with st.container(border=True):
                st.markdown(f"**{item['name']}** — `{item['query']}`")
                if st.button("Supprimer", key=f"del_search_{item['id']}"):
                    delete_search(item["id"])
                    st.rerun()
    else:
        st.info("Aucune recherche enregistrée.")

with tabs[3]:
    st.subheader("À propos")
    st.markdown("Application de suivi Vinted avec connecteur de recherche direct.")
