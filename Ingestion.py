from pymongo import MongoClient
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain_text_splitters import CharacterTextSplitter
from dotenv import load_dotenv
import os

load_dotenv()

# MongoDB Configuration
MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("DB_NAME")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")
INDEX_NAME = os.getenv("INDEX_NAME")

def load_documents(docs_path="docs"):
    """Load all text files from the docs directory"""
    print(f"Loading documents from {docs_path}...")
    
    if not os.path.exists(docs_path):
        raise FileNotFoundError(f"The directory {docs_path} does not exist. Please create it and add your company files.")
    
    loader = DirectoryLoader(
        path=docs_path,
        glob="*.txt",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"}
    )
    
    documents = loader.load()
    
    if len(documents) == 0:
        raise FileNotFoundError(f"No .txt files found in {docs_path}. Please add your company documents.")
    
    print(f"Loaded {len(documents)} documents.")
    return documents

def split_documents(documents, chunk_size=1000, chunk_overlap=100):
    """Split documents into smaller chunks"""
    print("Splitting documents into chunks...")
    text_splitter = CharacterTextSplitter(
        chunk_size=chunk_size, 
        chunk_overlap=chunk_overlap
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Created {len(chunks)} chunks.")
    return chunks

def create_vector_store(chunks):
    """Create and store embeddings in MongoDB Atlas using local HuggingFace model"""
    print("Creating local embeddings and storing in MongoDB Atlas...")
        
    # Using a popular, small, and fast local model
    embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    # Connect to MongoDB
    client = MongoClient(MONGODB_URI)
    collection = client[DB_NAME][COLLECTION_NAME]
    
    # Create MongoDB Vector Search
    vectorstore = MongoDBAtlasVectorSearch.from_documents(
        documents=chunks,
        embedding=embedding_model,
        collection=collection,
        index_name=INDEX_NAME
    )
    
    print("--- Finished storing in MongoDB ---")
    return vectorstore

def main():
    """Main ingestion pipeline"""
    print("=== RAG Document Ingestion Pipeline (MongoDB Atlas) ===\n")
    
    # Check if necessary environment variables are set
    if not all([MONGODB_URI, DB_NAME, COLLECTION_NAME, INDEX_NAME]):
        print("❌ Error: MongoDB environment variables are missing in .env")
        return

    docs_path = "docs"
    
    # Step 1: Load documents
    documents = load_documents(docs_path)  

    # Step 2: Split into chunks
    chunks = split_documents(documents)
    
    # Step 3: Create vector store in MongoDB
    create_vector_store(chunks)
    
    print("\n✅ Ingestion complete! Your documents are now in MongoDB Atlas.")
    print("💡 Used local 'all-MiniLM-L6-v2' embeddings (Free).")
    print("⚠️  IMPORTANT: Make sure your Vector Search Index has 384 dimensions (for all-MiniLM-L6-v2).")

if __name__ == "__main__":
    main()

if __name__ == "__main__":
    main()




# documents = [
#    Document(
#        page_content="Google LLC is an American multinational corporation and technology company focusing on online advertising, search engine technology, cloud computing, computer software, quantum computing, e-commerce, consumer electronics, and artificial intelligence (AI).",
#        metadata={'source': 'docs/google.txt'}
#    ),
#    Document(
#        page_content="Microsoft Corporation is an American multinational corporation and technology conglomerate headquartered in Redmond, Washington.",
#        metadata={'source': 'docs/microsoft.txt'}
#    ),
#    Document(
#        page_content="Nvidia Corporation is an American technology company headquartered in Santa Clara, California.",
#        metadata={'source': 'docs/nvidia.txt'}
#    ),
#    Document(
#        page_content="Space Exploration Technologies Corp., commonly referred to as SpaceX, is an American space technology company headquartered at the Starbase development site in Starbase, Texas.",
#        metadata={'source': 'docs/spacex.txt'}
#    ),
#    Document(
#        page_content="Tesla, Inc. is an American multinational automotive and clean energy company headquartered in Austin, Texas.",
#        metadata={'source': 'docs/tesla.txt'}
#    )
# ]


