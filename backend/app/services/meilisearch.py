 import logging
 
 from meilisearch import Client
 
 from app.config import settings
 from app.models.product import Product
 
 logger = logging.getLogger(__name__)
 
 INDEX_UID = settings.MEILISEARCH_INDEX
 
 
 def get_client() -> Client:
     return Client(settings.MEILISEARCH_HOST, settings.MEILISEARCH_API_KEY)
 
 
 def create_index():
     """Initialize Meilisearch index with searchable attributes."""
     client = get_client()
     try:
         client.create_index(INDEX_UID, {"primaryKey": "id"})
         index = client.index(INDEX_UID)
         index.update_searchable_attributes(["name", "brand", "notes", "category_name"])
         index.update_filterable_attributes(["family_id", "category_id", "is_active"])
         index.update_sortable_attributes(["updated_at", "price"])
         logger.info(f"Meilisearch index '{INDEX_UID}' initialized")
     except Exception as e:
         logger.warning(f"Meilisearch index init skipped: {e}")
 
 
 async def sync_product(product: Product, category_name: str | None = None):
     """Sync a single product to Meilisearch."""
     try:
         client = get_client()
         index = client.index(INDEX_UID)
         doc = {
             "id": product.id,
             "family_id": product.family_id,
             "category_id": product.category_id,
             "category_name": category_name or "",
             "name": product.name,
             "brand": product.brand or "",
             "specification": product.specification or "",
             "unit": product.unit,
             "notes": product.notes or "",
             "is_active": product.is_active,
             "updated_at": product.updated_at.isoformat() if product.updated_at else "",
         }
         index.add_documents([doc])
         logger.info(f"Product {product.id} synced to Meilisearch")
     except Exception as e:
         logger.error(f"Failed to sync product {product.id} to Meilisearch: {e}")
 
 
 async def remove_product(product_id: str):
     """Remove a product from Meilisearch index."""
     try:
         client = get_client()
         index = client.index(INDEX_UID)
         index.delete_document(product_id)
         logger.info(f"Product {product_id} removed from Meilisearch")
     except Exception as e:
         logger.error(f"Failed to remove product {product_id} from Meilisearch: {e}")
 
 
 async def search_products(family_id: str, query: str, limit: int = 20) -> list[dict]:
     """Search products in Meilisearch."""
     try:
         client = get_client()
         index = client.index(INDEX_UID)
         result = index.search(
             query,
             {
                 "filter": f"family_id = {family_id} AND is_active = true",
                 "limit": limit,
             },
         )
         return result.get("hits", [])
     except Exception as e:
         logger.error(f"Meilisearch search failed: {e}")
         return []
 
 
 async def search_all(query: str, limit: int = 20) -> list[dict]:
     """Search all products without family filter."""
     try:
         client = get_client()
         index = client.index(INDEX_UID)
         result = index.search(query, {"limit": limit})
         return result.get("hits", [])
     except Exception as e:
         logger.error(f"Meilisearch global search failed: {e}")
         return []
