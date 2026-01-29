# =====================================================
The Answer Generation module is responsible for producing the final user-facing response using a Large Language Model (LLM, powered by Groq) based strictly on the context retrieved from MongoDB Atlas.

After the Retriever returns the most relevant document chunks, this module combines them into a structured prompt along with the user’s question. This prompt explicitly instructs the LLM to answer only using the provided documents, ensuring responses remain grounded in the knowledge base.

The Groq-hosted LLaMA model then processes this context-aware prompt and generates a concise, accurate answer. If the required information is not present in the retrieved documents, the system is designed to respond that there is insufficient information, preventing hallucinated outputs.

In this project, the Answer Generator uses:

Groq’s llama-3.1-8b-instant model for fast inference

LangChain message abstractions (SystemMessage, HumanMessage) for structured prompting

Retrieved MongoDB Atlas vector search results as grounding context

This component completes the Retrieval-Augmented Generation (RAG) pipeline by transforming retrieved knowledge into natural language answers, enabling reliable, enterprise-grade question answering over custom documents.
# =====================================================

# -----------------------------
# Groq LLM
# -----------------------------
from langchain_groq import ChatGroq
# -----------------------------
# HuggingFace embeddings
# -----------------------------
from langchain_huggingface import HuggingFaceEmbeddings

# -----------------------------
# MongoDB client + Vector Search
# -----------------------------
from pymongo import MongoClient
from langchain_mongodb import MongoDBAtlasVectorSearch

# -----------------------------
# Load environment variables
# -----------------------------
from dotenv import load_dotenv
import os

load_dotenv()

# =====================================================
# Environment Configuration
# =====================================================

MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("DB_NAME")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")
INDEX_NAME = os.getenv("INDEX_NAME")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")


# =====================================================
# Function: get_vector_store
# Initializes MongoDB Atlas Vector Search
# =====================================================
def get_vector_store():

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
def retrieve_documents(query, k=5):

    vectorstore = get_vector_store()

    retriever = vectorstore.as_retriever(
        search_kwargs={"k": k}
    )

    print("Retrieving relevant documents...")

    docs = retriever.invoke(query)

    return docs


# =====================================================
# Function: generate_answer
# Uses Groq LLM to answer from retrieved context
# =====================================================
def generate_answer(query, docs):

    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY missing in .env")

    # Prepare context
    context_text = "\n".join([f"- {doc.page_content}" for doc in docs])

    combined_input = f"""
Based on the following documents, answer the question.

Question: {query}

Documents:
{context_text}

Only answer from the documents. If not found, say you don't have enough information.
"""

    print("Generating answer using Groq LLM...")

    model = ChatGroq(
        model="llama-3.1-8b-instant",
        groq_api_key=GROQ_API_KEY,
        temperature=0
    )

    messages = [
        SystemMessage(content="You are a helpful assistant."),
        HumanMessage(content=combined_input),
    ]

    result = model.invoke(messages)

    return result.content


# =====================================================
# Main Pipeline
# =====================================================
def main():

    print("=== RAG Generator Pipeline (MongoDB + Groq) ===\n")

    if not all([MONGODB_URI, DB_NAME, COLLECTION_NAME, INDEX_NAME]):
        print("❌ MongoDB environment variables missing.")
        return

    # Sample query (replace later with user input)
    query = "who is the CEO of NVIDIA in one line?"

    print(f"🔎 Query: {query}\n")

    # Step 1: Retrieve documents
    docs = retrieve_documents(query)

    if not docs:
        print("No relevant documents found.")
        return

    # Step 2: Generate answer
    try:
        answer = generate_answer(query, docs)

        print("\n--- Response ---\n")
        print(answer)

    except Exception as e:
        print(f"❌ Generation failed: {e}")


# =====================================================
# Entry Point
# =====================================================
if __name__ == "__main__":
    main()
