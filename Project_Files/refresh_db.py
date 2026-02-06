from pymongo import MongoClient
import os
from dotenv import load_dotenv
import subprocess

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = "remodel_catalog"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

colls_to_clear = ["unified_nodes", "embeddings", "embeddings_v1", "image_embeddings"]

print(f"--- REFRESHING DATABASE: {DB_NAME} ---")
for coll in colls_to_clear:
    if coll in db.list_collection_names():
        count = db[coll].count_documents({})
        print(f"Clearing {coll} ({count} documents)...")
        db[coll].delete_many({})

client.close()

print("\n--- RUNNING INGESTION ---")
# Run ingest.py
subprocess.run(["python", "ingest.py"], check=True)

print("\n✅ DATABASE REFRESH AND INGESTION COMPLETE!")
