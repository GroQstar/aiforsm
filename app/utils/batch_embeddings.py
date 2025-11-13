"""
Custom batch embedding wrapper to reduce API calls and stay within free tier limits.
Uses Gemini's batch embedding capability (100 chunks per API call) instead of individual calls.
"""
import os
import google.generativeai as genai
from typing import List
from dotenv import load_dotenv

class BatchGoogleGenerativeAIEmbeddings:
    """
    Custom embedding class that uses batch embedding to reduce API calls.
    Processes 100 chunks per API call instead of 1 chunk per call.
    """
    
    def __init__(self, model="models/text-embedding-004", google_api_key=None):
        # Load API key
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        env_path = os.path.join(project_root, '.env')
        load_dotenv(dotenv_path=env_path)
        load_dotenv()
        
        self.api_key = google_api_key or os.getenv('GOOGLE_API_KEY')
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY not found. Please set it in .env file.")
        
        self.model = model
        genai.configure(api_key=self.api_key)
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Embed multiple texts using batch processing.
        Processes up to 100 texts per API call to stay within quota limits.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors
        """
        if not texts:
            return []
        
        embeddings = []
        batch_size = 100  # Gemini supports up to 100 texts per batch
        
        # Process in batches
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            
            try:
                # Use Gemini's native batch embedding
                result = genai.embed_content(
                    model=self.model,
                    content=batch,  # Pass entire list
                    task_type="retrieval_document"
                )
                
                # Extract embeddings from batch result
                if isinstance(result, dict) and 'embedding' in result:
                    batch_embeddings = result['embedding']
                    if len(batch_embeddings) == len(batch):
                        embeddings.extend(batch_embeddings)
                    else:
                        raise ValueError(f"Expected {len(batch)} embeddings, got {len(batch_embeddings)}")
                else:
                    raise ValueError(f"Unexpected result format: {type(result)}")
                    
            except Exception as e:
                # If batch fails, try individual calls as fallback (slower but more reliable)
                print(f"Batch embedding failed, falling back to individual calls: {e}")
                for text in batch:
                    try:
                        result = genai.embed_content(
                            model=self.model,
                            content=text,
                            task_type="retrieval_document"
                        )
                        if isinstance(result, dict) and 'embedding' in result:
                            embeddings.append(result['embedding'])
                        else:
                            embeddings.append([])
                    except Exception as individual_error:
                        print(f"Failed to embed individual text: {individual_error}")
                        embeddings.append([])
        
        return embeddings
    
    def embed_query(self, text: str) -> List[float]:
        """
        Embed a single query text.
        
        Args:
            text: Query text to embed
            
        Returns:
            Embedding vector
        """
        try:
            result = genai.embed_content(
                model=self.model,
                content=text,
                task_type="retrieval_query"
            )
            
            if isinstance(result, dict) and 'embedding' in result:
                return result['embedding']
            else:
                raise ValueError(f"Unexpected result format: {type(result)}")
        except Exception as e:
            raise Exception(f"Error embedding query: {e}")

