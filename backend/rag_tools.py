import torch
from PIL import Image
from sentence_transformers import SentenceTransformer
from transformers import CLIPProcessor, CLIPModel


class RAGTools:

    def __init__(self):

        print("Loading Text Embedding Model (MiniLM)...")
        self.text_model = SentenceTransformer("all-MiniLM-L6-v2")  # 384 dims

        print("Loading CLIP Model...")
        self.clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        self.clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.clip_model.to(self.device)

        print("Models loaded.")


    # ---------------- Text Embeddings ----------------

    def get_embeddings(self, text: str):
        return self.text_model.encode(text).tolist()


    # ---------------- Chunking ----------------

    def get_chunks(self, text, chunk_size=500, overlap=100):

        words = text.split()
        chunks = []

        for i in range(0, len(words), chunk_size - overlap):
            chunk = " ".join(words[i:i + chunk_size])
            if chunk.strip():
                chunks.append(chunk)

        return chunks


    # ---------------- CLIP Image Embeddings ----------------

    def get_clip_image_embedding(self, image_path):

        image = Image.open(image_path).convert("RGB")

        inputs = self.clip_processor(images=image, return_tensors="pt").to(self.device)

        with torch.no_grad():
            emb = self.clip_model.get_image_features(**inputs)

        emb = emb / emb.norm(dim=-1, keepdim=True)

        return emb.cpu().numpy()[0].tolist()


    # ---------------- CLIP Text Embedding (Optional) ----------------

    def get_clip_text_embedding(self, text):

        inputs = self.clip_processor(text=[text], return_tensors="pt", padding=True).to(self.device)

        with torch.no_grad():
            emb = self.clip_model.get_text_features(**inputs)

        emb = emb / emb.norm(dim=-1, keepdim=True)

        return emb.cpu().numpy()[0].tolist()
