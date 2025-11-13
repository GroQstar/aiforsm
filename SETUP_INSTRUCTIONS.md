# Setup Instructions for RAG-ChatBot

## ✅ What's Done:
1. ✅ Cloned repository from `vitorccmanso/Rag-ChatBot`
2. ✅ Created `.env` file template (needs your API key)
3. ✅ Project structure ready

## ⚠️ Installation Issue:
The project uses `chromadb==0.4.24` which requires building `chroma-hnswlib` from source. This needs:
- **Microsoft Visual C++ Build Tools** (for Windows)

## 🔧 Solutions:

### Option 1: Install Visual C++ Build Tools (Recommended)
1. Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
2. Install "Desktop development with C++" workload
3. Then run: `pip install -r requirements.txt`

### Option 2: Update ChromaDB to newer version (Easier)
Update `requirements.txt` to use a newer ChromaDB version that has pre-built wheels:
- Change `chromadb==0.4.24` to `chromadb>=0.4.22` (or latest)

### Option 3: Use your existing working setup
Your old project already had ChromaDB 1.3.4 working! We could:
- Copy the working embedding logic from your old project
- Adapt this Streamlit UI to use your working backend

## 📝 Next Steps:
1. Add your Google API key to `.env` file:
   ```
   GOOGLE_API_KEY = "your_api_key_here"
   ```
2. Fix ChromaDB installation (choose one option above)
3. Run the app: `streamlit run app/app.py`

## 📂 Project Structure:
```
Aiforsm/
├── app/
│   ├── app.py              # Main Streamlit app
│   └── utils/
│       ├── chatbot.py      # Chat logic with LangChain
│       ├── prepare_vectordb.py  # ChromaDB setup
│       ├── save_docs.py    # Document processing
│       └── session_state.py # State management
├── docs/                   # PDF documents go here
├── .env                    # API key (needs your key)
└── requirements.txt        # Dependencies
```

## 🔍 Key Differences from Your Old Project:
- **UI**: Streamlit (web-based) vs Flask + React
- **Framework**: LangChain vs Direct API calls
- **Embedding Model**: `models/embedding-001` (old) vs `text-embedding-004` (new)
- **ChromaDB**: 0.4.24 (needs build tools) vs 1.3.4 (pre-built wheels)

