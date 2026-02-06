from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os

from .chat_engine import ChatEngine

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize ChatEngine
engine = ChatEngine()

class QuestionRequest(BaseModel):
    question: str

@app.post("/ask")
async def ask_question(request: QuestionRequest):
    print(f"MAIN_API: Received question: {request.question}")
    try:
        response = engine.ask(request.question)
        print(f"MAIN_API: Got response with {len(response.get('images', []))} images")
        return response
    except Exception as e:
        print(f"Error in /ask: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Mount data for access to PDFs
app.mount("/data", StaticFiles(directory="Data"), name="data")

# Mount images for access from HTML
app.mount("/images", StaticFiles(directory="Data/processed/images"), name="images")

# Serve the frontend at root - MOUNT THIS LAST so it doesn't intercept API routes
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)