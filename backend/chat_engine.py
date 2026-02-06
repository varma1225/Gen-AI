import os
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from .database import DatabaseHandler
from .rag_tools import RAGTools

class ChatEngine:
    def __init__(self):
        self.llm = ChatGroq(
            temperature=0,
            model_name="llama-3.1-8b-instant",
            api_key=os.getenv("GROQ_API_KEY")
        )
        self.db = DatabaseHandler()
        self.rag_tools = RAGTools()
        
        self.system_prompt = (
            "You are an expert interior design consultant. "
            "Use the provided context to answer the user's question. "
            "Be descriptive and helpful. If you mention specific products, use their names. "
            "\n\nContext:\n{context}"
        )
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("human", "{question}"),
        ])
        
        self.chain = self.prompt | self.llm | StrOutputParser()

    def ask(self, question: str):
        import numpy as np
        
        # 0. Relevance Guardrail
        q_lower = question.lower()
        # Fast check for obvious cases
        relevance_keywords = ["kitchen", "bedroom", "design", "remodel", "cabinets", "bed", "wardrobe", "pantry", "interior", "catalog"]
        is_obvious = any(kw in q_lower for kw in relevance_keywords)
        
        if not is_obvious:
            # Stronger check with LLM for edge cases
            check_prompt = (
                f"You are a triage agent for a Kitchen and Bedroom remodeling assistant. "
                f"Is the following query related to interior design, home remodeling, furniture, or specifically Kitchens/Bedrooms? "
                f"Query: '{question}'\n"
                f"Answer exactly 'YES' or 'NO'."
            )
            relevance_check = self.llm.invoke(check_prompt).content.strip().upper()
            if "NO" in relevance_check:
                return {
                    "answer": "We provide only the remodel designs of kitchen and bedroom. Please share your vision for your kitchen or bedroom!",
                    "images": []
                }

        # 1. Broadened Category Detection
        category = None
        
        kitchen_synonyms = ["kitchen", "cooking", "pantry", "hob", "cabinet", "dining", "sink"]
        bedroom_synonyms = ["bedroom", "bed", "sleep", "wardrobe", "queen", "king", "mattress", "dresser"]
        
        if any(s in q_lower for s in kitchen_synonyms): 
            category = "kitchen"
        elif any(s in q_lower for s in bedroom_synonyms): 
            category = "bedroom"

        # Keywords for regex fallback
        stop_words = {"show", "me", "find", "some", "the", "a", "an", "with", "for", "modern", "design", "designs", "ideas", "of", "in", "is", "where", "can", "i", "get"}
        words = q_lower.replace("?", "").replace(".", "").split()
        keywords = [w for w in words if w not in stop_words and len(w) > 2]
        
        # Remove category names from specific keywords for broad matching
        all_cat_synonyms = kitchen_synonyms + bedroom_synonyms
        specific_keywords = [kw for kw in keywords if kw not in all_cat_synonyms]
        if not specific_keywords: specific_keywords = keywords
            
        # 2. Get embeddings (Text & CLIP)
        query_emb = self.rag_tools.get_embeddings(question)
        
        refined_query = self._refine_query_for_clip(question)
        clip_query_emb = self.rag_tools.get_clip_text_embedding(refined_query)
        q_vec = np.array(clip_query_emb)
        
        # 3. UNIFIED SEARCH
        unified_results = []
        candidate_images = []
        seen_paths = set()
        
        u_filter = {"category": category} if category else None

        # SEARCH 1: Vector text search for context
        try:
            unified_results = self.db.unified_search(query_emb, limit=10, filter_dict=u_filter)
            print(f"DEBUG: Vector text search found {len(unified_results)} results")
        except Exception as e:
            print(f"DEBUG: Vector search failed: {e}")

        # SEARCH 2: CLIP-based for Visuals
        try:
            visual_results = self.db.strict_visual_search(clip_query_emb, category, limit=16)
            print(f"DEBUG: Strict visual search found {len(visual_results)} results for category: {category}")
            for doc in visual_results:
                for img_obj in doc.get("related_images", []):
                    # Hard Category Enforcement
                    img_cat = img_obj.get("category_source")
                    if category and img_cat and img_cat != category:
                        continue

                    img_emb = img_obj.get("clip_embedding")
                    path = img_obj.get("path")
                    if img_emb and path and path not in seen_paths:
                        # Re-calculate score for precision
                        i_vec = np.array(img_emb)
                        score = np.dot(q_vec, i_vec) / (np.linalg.norm(q_vec) * np.linalg.norm(i_vec) + 1e-8)
                        
                        if score > 0.25: # Higher Accuracy Threshold
                            full_pdf_path = img_obj.get("pdf_path", "").replace("\\", "/")
                            # Clean the path to work with the /data mount
                            clean_pdf_path = full_pdf_path.replace("Data/", "").replace("Data\\", "")
                            pg = img_obj.get("page_source")
                            pdf_url = f"http://localhost:8000/data/{clean_pdf_path}#page={pg}" if clean_pdf_path else None
                            
                            candidate_images.append({
                                "image_path": self._format_image_path(path),
                                "ocr_text": img_obj.get("ocr_text", ""),
                                "score": float(score),
                                "page": pg,
                                "pdf": img_cat or doc.get("category"),
                                "pdf_url": pdf_url
                            })
                            seen_paths.add(path)
        except Exception as e:
            print(f"DEBUG: CLIP visual search failed: {e}")

        # REGEX FALLBACK (If Vector yields nothing)
        if not unified_results and specific_keywords:
            print(f"DEBUG: Falling back to REGEX search for: {specific_keywords}")
            regex_queries = [{"combined_text": {"$regex": kw, "$options": "i"}} for kw in specific_keywords]
            regex_query = {"$or": regex_queries}
            if category: regex_query = {"$and": [regex_query, {"category": category}]}
                
            try:
                unified_results = list(self.db.unified_collection.find(regex_query).limit(10))
            except Exception as e:
                print(f"DEBUG: Regex fallback failed: {e}")

        # 4. Final Fallback: Featured samples
        if not unified_results:
            try: 
                fallback_filter = {"category": category} if category else {}
                unified_results = list(self.db.unified_collection.find(fallback_filter).limit(4))
            except: pass

        # 5. Extract Context and Additional Images
        context_parts = []
        for doc in unified_results:
            context_parts.append(doc.get("combined_text", ""))
            
            # Pick best images from text matches
            for img_obj in doc.get("related_images", []):
                # Hard Category Enforcement
                img_cat = img_obj.get("category_source")
                if category and img_cat and img_cat != category:
                    continue

                path = img_obj.get("path")
                if path and path not in seen_paths:
                    img_emb = img_obj.get("clip_embedding")
                    score = 0.22 # Default score for text match if no embedding
                    if img_emb:
                        i_vec = np.array(img_emb)
                        score = np.dot(q_vec, i_vec) / (np.linalg.norm(q_vec) * np.linalg.norm(i_vec) + 1e-8)
                    
                    if score > 0.22: # Higher threshold for linked images
                        full_pdf_path = img_obj.get("pdf_path", "").replace("\\", "/")
                        clean_pdf_path = full_pdf_path.replace("Data/", "").replace("Data\\", "")
                        pg = img_obj.get("page_source")
                        pdf_url = f"http://localhost:8000/data/{clean_pdf_path}#page={pg}" if clean_pdf_path else None

                        candidate_images.append({
                            "image_path": self._format_image_path(path),
                            "ocr_text": img_obj.get("ocr_text", ""),
                            "score": float(score),
                            "page": pg,
                            "pdf": img_cat or doc.get("category"),
                            "pdf_url": pdf_url
                        })
                        seen_paths.add(path)

        context = "\n\n".join(context_parts) if context_parts else "No specific catalog items found."
        
        # 6. Sort and Filter candidate images by score
        candidate_images.sort(key=lambda x: x["score"], reverse=True)
        final_images = candidate_images[:12]

        # 7. Generate Answer
        try:
            answer = self.chain.invoke({"context": context, "question": question})
        except Exception as e:
            answer = "I'm sorry, I'm having trouble with my architectural brain right now."

        return {
            "answer": answer,
            "images": final_images
        }

    def _refine_query_for_clip(self, query: str) -> str:
        q = query.lower()
        if not any(x in q for x in ["photo", "image", "design", "interior", "look"]):
            return f"An interior design photo of {query}"
        return query

    def _format_image_path(self, path: str):
        clean_path = path.replace("\\", "/")
        if "images/" in clean_path:
            filename = clean_path.split("images/")[-1]
            return f"images/{filename}"
        return clean_path
