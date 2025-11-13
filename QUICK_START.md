# Quick Start Guide

## ✅ Setup Complete!

### What's Been Done:
1. ✅ **Updated ChromaDB** - Changed from `0.4.24` to `>=0.4.22` (uses your existing 1.3.4)
2. ✅ **PDF Moved** - `Amazon-2024-Annual-Report.pdf` is in `docs/` folder
3. ✅ **Auto-Load Enabled** - Documents in `docs/` will be automatically processed on startup
4. ✅ **Dependencies Installed** - All packages installed successfully

### This is a **Streamlit** App (not Flask+React)
- Web-based UI using Streamlit framework
- Runs in your browser
- No separate frontend/backend setup needed

## 🚀 How to Run:

```bash
cd F:\Projects\Aiforsm
streamlit run app/app.py
```

The app will:
1. **Auto-detect** PDFs in `docs/` folder
2. **Auto-process** them on first startup (creates vector database)
3. **Auto-load** existing vector database on subsequent startups
4. Open in your browser automatically

## 📁 Project Structure:
```
Aiforsm/
├── app/
│   ├── app.py              # Main Streamlit app
│   └── utils/
│       ├── chatbot.py      # Chat logic
│       ├── prepare_vectordb.py  # ChromaDB setup
│       ├── save_docs.py    # Document processing
│       └── session_state.py # State management
├── docs/                   # Your PDFs go here
│   └── Amazon-2024-Annual-Report.pdf
├── Vector_DB - Documents/   # Auto-created (persistent storage)
├── .env                    # Your API key (already added)
└── requirements.txt        # Dependencies
```

## 🔑 Features:
- **Persistent Storage**: Vector database persists between sessions
- **Auto-Load**: Documents in `docs/` are automatically available
- **Chat History**: Remembers last 10 messages
- **Source Citations**: Shows which pages/documents answers come from

## 📝 Notes:
- First run will take time to embed the PDF (few minutes)
- Subsequent runs are instant (loads from persistent DB)
- You can add more PDFs via the sidebar upload button

