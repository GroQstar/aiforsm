from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from dotenv import load_dotenv
from utils.batch_embeddings import BatchGoogleGenerativeAIEmbeddings
import os
import chromadb
import warnings
import logging

# Suppress ChromaDB tenant warnings (harmless when using local PersistentClient)
chromadb_logger = logging.getLogger("chromadb")
chromadb_logger.setLevel(logging.ERROR)  # Only show errors, not warnings
warnings.filterwarnings("ignore", category=UserWarning, module="chromadb")

def extract_pdf_text(pdfs):
    """
    Extract text from PDF documents

    Parameters:
    - pdfs (list): List of PDF documents

    Returns:
    - docs: List of text extracted from PDF documents
    """
    docs = []
    for pdf in pdfs:
        pdf_path = os.path.join("docs", pdf)
        # Load text from the PDF and extend the list of documents
        docs.extend(PyPDFLoader(pdf_path).load())
    return docs

def get_text_chunks(docs):
    """
    Split text into chunks

    Parameters:
    - docs (list): List of text documents

    Returns:
    - chunks: List of text chunks
    """
    # Chunk size is configured to be an approximation to the model limit of 2048 tokens
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=8000, chunk_overlap=800, separators=["\n\n", "\n", " ", ""])
    chunks = text_splitter.split_documents(docs)
    return chunks

def get_vectorstore(pdfs, from_session_state=False):
    """
    Create or retrieve a vectorstore from PDF documents

    Parameters:
    - pdfs (list): List of PDF documents
    - from_session_state (bool, optional): Flag indicating whether to load from session state. Defaults to False

    Returns:
    - vectordb or None: The created or retrieved vectorstore. Returns None if loading from session state and the database does not exist
    """
    # Load .env from project root
    # Get the project root (F:\Projects\Aiforsm)
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    env_path = os.path.join(project_root, '.env')
    load_dotenv(dotenv_path=env_path)
    # Also try loading from current directory as fallback
    load_dotenv()
    # Get API key from environment
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found in environment. Please add it to your .env file.")
    
    # Use batch embedding to reduce API calls and stay within free tier quota
    # This processes 100 chunks per API call instead of 1 chunk per call
    # Reduces API calls from 50-100 to just 1-2 calls!
    embedding = BatchGoogleGenerativeAIEmbeddings(
        model="models/text-embedding-004",  # Use newer embedding model
        google_api_key=api_key
    )
    if from_session_state and os.path.exists("Vector_DB - Documents"):
        # Retrieve vectorstore from existing one
        # Use PersistentClient for local persistence (fixes tenant error)
        # Suppress tenant warnings - they're harmless for local file storage
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            client = chromadb.PersistentClient(path="Vector_DB - Documents")
        vectordb = Chroma(client=client, embedding_function=embedding)
        
        # Check if all PDFs in docs folder are in the vector DB
        # Get list of documents currently in vector DB
        try:
            existing_collection = client.get_collection(name="langchain")
            existing_docs = set()
            if existing_collection.count() > 0:
                items = existing_collection.get(limit=10000)  # Get all items
                if items and 'metadatas' in items:
                    for metadata in items['metadatas']:
                        source = metadata.get('source', '')
                        # Extract filename from path (e.g., "docs\file.pdf" -> "file.pdf")
                        if source.startswith('docs\\') or source.startswith('docs/'):
                            filename = os.path.basename(source)
                            existing_docs.add(filename)
            
            # Check if all PDFs in docs folder are in the vector DB
            missing_docs = []
            for pdf in pdfs:
                if pdf not in existing_docs:
                    missing_docs.append(pdf)
            
            if missing_docs:
                # Some documents are missing - need to reprocess
                import streamlit as st
                with st.sidebar:
                    st.warning(f"⚠️ Found {len(missing_docs)} new document(s) not in database. Reprocessing...")
                # Fall through to reprocess all documents
                return None
            else:
                # All documents are in the vector DB
                return vectordb
        except Exception as e:
            # If we can't check, just return the existing vector DB
            # (better to use existing DB than fail completely)
            return vectordb
    elif not from_session_state:
        import streamlit as st
        # Show progress in sidebar for better visibility
        with st.sidebar:
            st.subheader("📊 Processing Status")
            progress_bar = st.progress(0)
            status_text = st.empty()
        
        try:
            status_text.text("📄 Step 1/4: Extracting text from PDF...")
            progress_bar.progress(10)
            docs = extract_pdf_text(pdfs)
            
            status_text.text(f"✂️ Step 2/4: Chunking text into {len(docs)} pages...")
            progress_bar.progress(30)
            chunks = get_text_chunks(docs)
            
            status_text.text(f"🔢 Step 3/4: Generating embeddings for {len(chunks)} chunks...")
            progress_bar.progress(50)
            status_text.text(f"⏱️ This takes ~10-20 seconds with batch processing (not 5 minutes!)")
            
            # Create vectorstore from chunks and saves it to the folder Vector_DB - Documents
            # Use PersistentClient for local persistence (fixes tenant error)
            # Suppress tenant warnings - they're harmless for local file storage
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                client = chromadb.PersistentClient(path="Vector_DB - Documents")
            vectordb = Chroma.from_documents(documents=chunks, embedding=embedding, client=client)
            
            status_text.text("💾 Step 4/4: Saving to database...")
            progress_bar.progress(90)
            
            status_text.text(f"✅ Complete! Processed {len(chunks)} chunks")
            progress_bar.progress(100)
            
            # Show success message in main area
            st.success(f"✅ **Successfully processed {len(pdfs)} document(s)!** You can now start chatting below.")
            
            return vectordb
        except Exception as e:
            progress_bar.progress(0)
            if "quota" in str(e).lower() or "429" in str(e):
                status_text.text("❌ Quota Exceeded")
                st.error("""
                **🚫 Quota Limit Reached** 
                
                Your free tier quota has been exceeded. You have two options:
                1. **Wait 24 hours** for quota reset, then restart the app
                2. **Upgrade to paid tier** at https://ai.google.dev/pricing
                
                The app is configured to use batch embedding (1-2 API calls instead of 50-100), 
                so once quota resets, processing will be fast (~10-20 seconds) and stay within limits.
                """)
            else:
                status_text.text(f"❌ Error: {str(e)[:100]}")
                st.error(f"**Error processing documents:** {str(e)}")
            raise
    return None