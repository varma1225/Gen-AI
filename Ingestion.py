## Why This Pipeline Is Used and How It Works

This pipeline is used to build a Retrieval-Augmented Generation (RAG) knowledge base by converting company documents into searchable vector embeddings stored in MongoDB Atlas.
Instead of relying only on a language model’s memory, this approach allows applications to retrieve accurate, up-to-date information directly from custom documents such as policies, 
manuals, or FAQs. The system works by first loading all text files from a local folder, then splitting large documents into smaller overlapping chunks to preserve context. 
Each chunk is converted into numerical embeddings using a local HuggingFace model, and these vectors are stored in MongoDB Atlas using Vector Search. 
When a user later asks a question, MongoDB performs semantic similarity search on these embeddings to find the most relevant document chunks,
which can then be passed to an LLM to generate precise, context-aware answers.
This approach improves accuracy, reduces hallucinations, and enables scalable enterprise search and chatbot applications.
# -----------------------------
# Import MongoDB client to connect to MongoDB Atlas
# -----------------------------
from pymongo import MongoClient

# -----------------------------
# MongoDB Atlas Vector Search integration from LangChain
# Used to store embeddings and perform similarity search
# -----------------------------
from langchain_mongodb import MongoDBAtlasVectorSearch

# -----------------------------
# HuggingFace embeddings
# Used to convert text into numerical vectors locally (no OpenAI API)
# -----------------------------
from langchain_huggingface import HuggingFaceEmbeddings

# -----------------------------
# TextLoader loads a single text file
# DirectoryLoader loads multiple files from a folder
# -----------------------------
from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders import DirectoryLoader

# -----------------------------
# CharacterTextSplitter breaks large documents into smaller chunks
# This improves embedding quality and retrieval accuracy
# -----------------------------
from langchain_text_splitters import CharacterTextSplitter

# -----------------------------
# Loads environment variables from .env file
# -----------------------------
from dotenv import load_dotenv

# -----------------------------
# OS module used for:
# - Reading environment variables
# - Checking folder existence
# - Handling file paths
# -----------------------------
import os

# Load all environment variables from .env file into the system
load_dotenv()

# =====================================================
# MongoDB Configuration
# These values are read from .env file
# =====================================================

# MongoDB Atlas connection URI
MONGODB_URI = os.getenv("MONGODB_URI")

# Database name
DB_NAME = os.getenv("DB_NAME")

# Collection where vectors will be stored
COLLECTION_NAME = os.getenv("COLLECTION_NAME")

# MongoDB Atlas Vector Search index name
INDEX_NAME = os.getenv("INDEX_NAME")


# =====================================================
# Function: load_documents
# Loads all .txt files from docs directory
# =====================================================
def load_documents(docs_path="docs"):
    """
    Loads all text documents from the specified folder.
    """

    print(f"Loading documents from {docs_path}...")

    # Check whether docs folder exists
    if not os.path.exists(docs_path):
        raise FileNotFoundError(
            f"The directory {docs_path} does not exist. Please create it and add your company files."
        )

    # DirectoryLoader reads multiple .txt files
    loader = DirectoryLoader(
        path=docs_path,              # Folder path
        glob="*.txt",               # Load only .txt files
        loader_cls=TextLoader,      # Use TextLoader for each file
        loader_kwargs={"encoding": "utf-8"}  # UTF-8 encoding
    )

    # Load documents into LangChain Document objects
    documents = loader.load()

    # If no documents found, throw error
    if len(documents) == 0:
        raise FileNotFoundError(
            f"No .txt files found in {docs_path}. Please add your company documents."
        )

    print(f"Loaded {len(documents)} documents.")

    return documents


# =====================================================
# Function: split_documents
# Breaks documents into smaller overlapping chunks
# =====================================================
def split_documents(documents, chunk_size=1000, chunk_overlap=100):
    """
    Splits documents into smaller chunks for embedding.
    """

    print("Splitting documents into chunks...")

    # CharacterTextSplitter splits text based on character count
    text_splitter = CharacterTextSplitter(
        chunk_size=chunk_size,       # Size of each chunk
        chunk_overlap=chunk_overlap # Overlap between chunks for context
    )

    # Perform splitting
    chunks = text_splitter.split_documents(documents)

    print(f"Created {len(chunks)} chunks.")

    return chunks


# =====================================================
# Function: create_vector_store
# Converts text chunks into embeddings and stores them in MongoDB
# =====================================================
def create_vector_store(chunks):
    """
    Generates embeddings locally and stores them in MongoDB Atlas.
    """

    print("Creating local embeddings and storing in MongoDB Atlas...")

    # Initialize HuggingFace embedding model
    # all-MiniLM-L6-v2 is fast and lightweight
    embedding_model = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2"
    )

    # Connect to MongoDB Atlas using URI
    client = MongoClient(MONGODB_URI)

    # Select database and collection
    collection = client[DB_NAME][COLLECTION_NAME]

    # Create vector store in MongoDB Atlas
    # This converts text into vectors and saves them
    vectorstore = MongoDBAtlasVectorSearch.from_documents(
        documents=chunks,           # Document chunks
        embedding=embedding_model,  # Embedding model
        collection=collection,      # MongoDB collection
        index_name=INDEX_NAME       # Vector Search index
    )

    print("--- Finished storing in MongoDB ---")

    return vectorstore


# =====================================================
# Main pipeline
# Controls full ingestion workflow
# =====================================================
def main():
    """
    Complete RAG ingestion pipeline:
    Load → Split → Embed → Store
    """

    print("=== RAG Document Ingestion Pipeline (MongoDB Atlas) ===\n")

    # Verify environment variables exist
    if not all([MONGODB_URI, DB_NAME, COLLECTION_NAME, INDEX_NAME]):
        print("❌ Error: MongoDB environment variables are missing in .env")
        return

    # Folder containing company documents
    docs_path = "docs"

    # Step 1: Load documents from folder
    documents = load_documents(docs_path)

    # Step 2: Split documents into chunks
    chunks = split_documents(documents)

    # Step 3: Generate embeddings and store in MongoDB
    create_vector_store(chunks)

    print("\n✅ Ingestion complete! Your documents are now in MongoDB Atlas.")


# =====================================================
# Entry point of Python script
# =====================================================
if __name__ == "__main__":
    main()

