"""Gabarit pour un fournisseur de données ayant un accès autorisé et documenté.

Ne pas y ajouter de scraping non autorisé, de contournement de protections
ou d'utilisation d'API privées sans permission. Implémenter uniquement après
validation contractuelle et technique du fournisseur.
"""

class AuthorizedProvider:
    name = "authorized_provider_template"

    def __init__(self, api_key: str):
        self.api_key = api_key

    def search(self, query: str, filters: dict) -> list[dict]:
        """Retourne des annonces normalisées selon le schéma ci-dessous."""
        raise NotImplementedError(
            "Connecteur non configuré : renseigner ici l'API documentée du fournisseur."
        )

# Schéma attendu par l'application :
# {
#   "listing_id": "identifiant stable",
#   "title": "Titre de l'annonce",
#   "price": 42.0,
#   "condition": "Très bon état",
#   "shipping_cost": 3.99,  # None si indisponible
#   "date_published": "2026-11-14",
#   "url": "https://...",
#   "image_url": "https://...",
#   "source": "nom_du_fournisseur"
# }
