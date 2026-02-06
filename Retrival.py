# =====================================================
The Retriever is responsible for finding the most relevant document chunks from MongoDB Atlas based on a user’s query.

It works by first converting the user’s question into a vector embedding using the same HuggingFace model that was used during ingestion. This ensures both queries and documents exist in the same semantic vector space.

Once the query is embedded, MongoDB Atlas Vector Search performs a similarity search against the stored document embeddings and returns the top-K closest matches. These retrieved chunks represent the most contextually relevant information related to the user’s question.

The Retriever acts as the bridge between the Vector Database and the Language Model. Instead of sending the entire knowledge base to the LLM, only the most relevant pieces of information are selected and passed forward. This significantly improves response accuracy, reduces hallucinations, and keeps the system efficient and scalable.

In this project, the Retriever uses:

HuggingFace all-MiniLM-L6-v2 for query embeddings

MongoDB Atlas Vector Search for semantic similarity retrieval

LangChain’s retriever interface for clean integration

This component enables real-time semantic search over custom documents and forms the core of the Retrieval-Augmented Generation (RAG) pipeline.
# =====================================================

# -----------------------------
# MongoDB client
# -----------------------------
from pymongo import MongoClient

# -----------------------------
# MongoDB Atlas Vector Search
# -----------------------------
from langchain_mongodb import MongoDBAtlasVectorSearch

# -----------------------------
# HuggingFace embeddings
# -----------------------------
from langchain_huggingface import HuggingFaceEmbeddings

# -----------------------------
# Load environment variables
# -----------------------------
from dotenv import load_dotenv
import os

load_dotenv()

# =====================================================
# MongoDB Configuration
# =====================================================

MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("DB_NAME")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")
INDEX_NAME = os.getenv("INDEX_NAME")


# =====================================================
# Function: get_vector_store
# Connects to MongoDB Atlas vector collection
# =====================================================
def get_vector_store():
    """
    Initializes embedding model and MongoDB vector store.
    """

    print("Connecting to MongoDB Atlas Vector Search...")

    embedding_model = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2"
    )

    client = MongoClient(MONGODB_URI)
    collection = client[DB_NAME][COLLECTION_NAME]

    vectorstore = MongoDBAtlasVectorSearch(
        collection=collection,
        embedding=embedding_model,
        index_name=INDEX_NAME
    )

    return vectorstore


# =====================================================
# Function: retrieve_documents
# Performs semantic similarity search
# =====================================================
def retrieve_documents(query, k=1):
    """
    Retrieves top K relevant document chunks.
    """

    vectorstore = get_vector_store()

    retriever = vectorstore.as_retriever(
        search_kwargs={"k": k}
    )

    print("Performing semantic search...")

    docs = retriever.invoke(query)

    return docs


# =====================================================
# Main Pipeline
# =====================================================
def main():

    print("=== RAG Retrieval Pipeline (MongoDB Atlas) ===\n")

    # Validate env variables
    if not all([MONGODB_URI, DB_NAME, COLLECTION_NAME, INDEX_NAME]):
        print("❌ MongoDB environment variables missing.")
        return

    # Sample query (replace with user input later)
    query = "who is the CEO of NVIDIA ?"

    print(f"User Query: {query}\n")

    # Retrieve documents
    relevant_docs = retrieve_documents(query)

    # Display results
    print("--- Context ---\n")

    if not relevant_docs:
        print("No relevant documents found.")
        return

    for i, doc in enumerate(relevant_docs, 1):
        print(f"Document {i}:\n{doc.page_content}\n")


# =====================================================
# Entry Point
# =====================================================
if __name__ == "__main__":
    main()
