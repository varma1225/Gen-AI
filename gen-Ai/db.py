from pymongo import MongoClient

client=MongoClient("mongodb+srv://varma:varma1225@varma.f5zdh.mongodb.net/?appName=varma")
db=client["gen-Ai-basic"]
collection=db["embeddings"]