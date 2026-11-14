# Vinted Tracker

Application Streamlit de recherche et de suivi multi-sources.

## Fonctionnalités incluses
- Recherche libre sur les annonces importées (mode souple : au moins un terme du titre correspond).
- Filtres par état, prix minimum/maximum et mots exclus.
- Tri croissant/décroissant par date, prix, frais d'envoi, total, état ou titre.
- Pagination 10 / 25 / 50 / 100.
- Import CSV, ajout manuel, historique SQLite et recherches surveillées.
- Connecteur fournisseur sous forme de gabarit.

## Lancement local
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Déploiement Streamlit Community Cloud
1. Crée un dépôt GitHub et ajoute tous les fichiers.
2. Dans Streamlit Community Cloud, crée une application depuis ce dépôt.
3. Choisis `app.py` comme fichier principal.
4. Déploie.

## Format CSV
Colonnes obligatoires : `listing_id,title,price`

Colonnes facultatives : `condition,shipping_cost,date_published,url,image_url,source`

Exemple :
```csv
listing_id,title,price,condition,shipping_cost,date_published,url,image_url,source
item-001,Miniature Teclis,42,Très bon état,3.99,2026-11-14,https://exemple.fr/annonce,,import_csv
```

## Connecter une source de données
Le fichier `connectors/provider_template.py` décrit le contrat attendu. Implémente un fournisseur uniquement si son accès aux données Vinted est explicitement autorisé et documenté. Ne pas utiliser de scraping interdit, de contournement de protections ou d'API privées sans autorisation.

## Limites importantes
- Cette version ne récupère pas directement les annonces Vinted.
- L'import CSV et la saisie manuelle servent à valider l'interface et le moteur.
- Les frais d'envoi restent `indisponibles` s'ils ne sont pas fournis par la source.
- Le stockage SQLite local peut être éphémère sur Streamlit Community Cloud. Pour un suivi persistant en production, prévoir une base externe (PostgreSQL ou équivalent).
- Le workflow GitHub est un squelette : il ne lance pas encore de recherche en direct, car aucun fournisseur autorisé n'est configuré.
