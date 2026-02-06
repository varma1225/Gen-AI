from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

class DatabaseHandler:
    def __init__(self, uri: str = None, db_name: str = "remodel_catalog"):
        self.uri = uri or os.getenv("MONGO_URI")
        print(f"Connecting to MongoDB with URI: {self.uri}")
        self.client = MongoClient(self.uri)
        self.db = self.client[db_name]
        self.embeddings = self.db.embeddings_v1
        self.image_embeddings = self.db.image_embeddings
        self.unified_collection = self.db.unified_nodes

    def vector_search(self, query_embedding, limit=5, filter_dict=None):
        search_params = {
            "index": "vector_index",
            "path": "embedding",
            "queryVector": query_embedding,
            "numCandidates": 100,
            "limit": limit
        }
        if filter_dict:
            search_params["filter"] = filter_dict
            
        pipeline = [{"$vectorSearch": search_params}]
        return list(self.embeddings.aggregate(pipeline))

    def get_images_by_link_id(self, link_id):
        return list(self.image_embeddings.find({"link_id": link_id}))

    def visual_search(self, clip_embedding, limit=5, filter_dict=None):
        search_params = {
            "index": "image_vector_index",
            "path": "embedding",
            "queryVector": clip_embedding,
            "numCandidates": 100,
            "limit": limit
        }
        if filter_dict:
            search_params["filter"] = filter_dict

        pipeline = [{"$vectorSearch": search_params}]
        return list(self.image_embeddings.aggregate(pipeline))

    def unified_search(self, query_embedding, limit=5, filter_dict=None):
        search_params = {
            "index": "vector_index", 
            "path": "embedding",
            "queryVector": query_embedding,
            "numCandidates": 100,
            "limit": limit
        }
        if filter_dict:
            search_params["filter"] = filter_dict
            
        pipeline = [{"$vectorSearch": search_params}]
        return list(self.unified_collection.aggregate(pipeline))

    def strict_visual_search(self, clip_text_embedding, category, limit=5):
        """
        Search with hard category filtering at the vector index level.
        """
        search_params = {
            "index": "unified_clip_index",
            "path": "related_images.clip_embedding",
            "queryVector": clip_text_embedding,
            "numCandidates": 100,
            "limit": limit
        }
        if category:
            search_params["filter"] = {"category": category}
            
        pipeline = [{"$vectorSearch": search_params}]
        return list(self.unified_collection.aggregate(pipeline))
