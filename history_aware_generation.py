# =====================================================
For each user interaction, the system performs the following steps:

Rewrites the user’s question using prior conversation history to make it independent and optimized for semantic search.

Converts the rewritten query into embeddings using HuggingFace and retrieves the most relevant document chunks from MongoDB Atlas Vector Search.

Combines the retrieved context with the original user question.

Sends this grounded prompt to Groq’s LLaMA model to generate a clear, accurate response.

Stores both user messages and assistant replies to preserve conversational continuity across turns.
# =====================================================

# -----------------------------
# MongoDB + Vector Search
# -----------------------------
from pymongo import MongoClient
from langchain_mongodb import MongoDBAtlasVectorSearch

# -----------------------------
# LangChain Messages
# -----------------------------
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

# -----------------------------
# Embeddings + Groq LLM
# -----------------------------
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq

# -----------------------------
# Environment variables
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
# Global Objects
# =====================================================

chat_history = []


# =====================================================
# Function: get_vector_store
# Initializes MongoDB Atlas Vector Search
# =====================================================
def get_vector_store():

    embeddings = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2"
    )

    client = MongoClient(MONGODB_URI)
    collection = client[DB_NAME][COLLECTION_NAME]

    vectorstore = MongoDBAtlasVectorSearch(
        collection=collection,
        embedding=embeddings,
        index_name=INDEX_NAME
    )

    return vectorstore


# =====================================================
# Function: get_llm
# Initializes Groq LLM
# =====================================================
def get_llm():

    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY missing in .env")

    model = ChatGroq(
        model="llama-3.1-8b-instant",
        groq_api_key=GROQ_API_KEY,
        temperature=0
    )

    return model


# =====================================================
# Function: rewrite_question
# Makes follow-up questions standalone
# =====================================================
def rewrite_question(model, user_question):

    if not chat_history:
        return user_question

    messages = [
        SystemMessage(content="Given the chat history, rewrite the new question to be standalone and searchable. Just return the rewritten question."),
    ] + chat_history + [
        HumanMessage(content=f"New question: {user_question}")
    ]

    result = model.invoke(messages)

    return result.content.strip()


# =====================================================
# Function: retrieve_documents
# Performs semantic search
# =====================================================
def retrieve_documents(query, k=3):

    vectorstore = get_vector_store()

    retriever = vectorstore.as_retriever(
        search_kwargs={"k": k}
    )

    docs = retriever.invoke(query)

    return docs


# =====================================================
# Function: generate_answer
# Uses Groq to answer based on retrieved context
# =====================================================
def generate_answer(model, user_question, docs):

    context = "\n".join([f"- {doc.page_content}" for doc in docs])

    combined_input = f"""
Based on the following documents, please answer this question:

Question: {user_question}

Documents:
{context}

Please provide a clear answer using ONLY the documents.
If not found, say you don't have enough information.
"""

    messages = [
        SystemMessage(content="You are a helpful assistant that answers questions based on provided documents and conversation history."),
    ] + chat_history + [
        HumanMessage(content=combined_input)
    ]

    result = model.invoke(messages)

    return result.content


# =====================================================
# Function: ask_question
# Full conversational RAG flow
# =====================================================
def ask_question(model, user_question):

    print(f"\n--- You asked: {user_question} ---")

    # Step 1: Rewrite question
    search_question = rewrite_question(model, user_question)
    print(f"🔍 Searching for: {search_question}")

    # Step 2: Retrieve documents
    docs = retrieve_documents(search_question)

    print(f"📄 Found {len(docs)} relevant documents")

    # Step 3: Generate answer
    answer = generate_answer(model, user_question, docs)

    # Step 4: Store conversation
    chat_history.append(HumanMessage(content=user_question))
    chat_history.append(AIMessage(content=answer))

    print(f"\n✨ Response: {answer}")

    return answer


# =====================================================
# Chat Loop
# =====================================================
def start_chat():

    print("\n🚀 Starting Conversational RAG Assistant (Groq + MongoDB)")
    print("Type 'quit' to exit.")

    if not all([MONGODB_URI, DB_NAME, COLLECTION_NAME, INDEX_NAME]):
        print("❌ MongoDB environment variables missing.")
        return

    try:
        model = get_llm()
    except Exception as e:
        print(e)
        return

    while True:

        question = input("\nYour question: ").strip()

        if not question:
            continue

        if question.lower() in ["quit", "exit"]:
            print("Goodbye!")
            break

        try:
            ask_question(model, question)
        except Exception as e:
            print(f"❌ Error: {e}")


# =====================================================
# Entry Point
# =====================================================
if __name__ == "__main__":
    start_chat()
