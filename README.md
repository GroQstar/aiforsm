# RAG ChatBot

A Retrieval-Augmented Generation (RAG) chatbot that allows you to chat with PDF documents using Google's Gemini-Pro model, LangChain, and ChromaDB.

## Features

- **Upload Documents**: Upload PDF documents and chat with them instantly
- **Persistent Storage**: Documents are automatically saved and loaded on subsequent sessions
- **Chat History**: Maintains conversation context (last 10 messages)
- **Source Citations**: Shows which pages/documents answers come from
- **Auto-Load**: Documents in `docs/` folder are automatically processed on startup

## Prerequisites

- Python 3.8+
- Google Gemini API key ([Get one here](https://aistudio.google.com/app/apikey))

## Setup

### 1. Clone the repository
```bash
git clone <repository-url>
cd Aiforsm
```

### 2. Create `.env` file
Create a `.env` file in the root directory:
```
GOOGLE_API_KEY=your_api_key_here
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the application
```bash
streamlit run app/app.py
```

The app will automatically open in your browser.

## Project Structure

```
Aiforsm/
├── app/
│   ├── app.py              # Main Streamlit application
│   └── utils/
│       ├── chatbot.py      # Chat logic with LangChain
│       ├── prepare_vectordb.py  # ChromaDB setup
│       ├── save_docs.py    # Document processing
│       └── session_state.py # State management
├── docs/                   # PDF documents go here
├── Vector_DB - Documents/  # Auto-created (persistent vector storage)
├── .env                    # API key configuration
└── requirements.txt        # Python dependencies
```

## How It Works

1. **Upload PDF**: Documents are saved to the `docs/` folder
2. **Text Chunking**: PDF text is extracted and split into chunks
3. **Embedding**: Text chunks are converted to vector embeddings using Gemini
4. **Vector Storage**: Embeddings are stored in ChromaDB (persistent on disk)
5. **Query Processing**: When you ask a question:
   - Your question is embedded
   - Similar document chunks are retrieved from the vector database
   - Relevant chunks + your question are sent to Gemini-Pro
   - Response is generated based on the document content

## Usage

1. **First Run**: Upload a PDF via the sidebar. Processing takes a few minutes.
2. **Subsequent Runs**: Documents in `docs/` are automatically loaded (instant).
3. **Ask Questions**: Type your question and get answers based on your documents.
4. **View Sources**: Check the sidebar to see which pages your answers come from.

## Troubleshooting

### "Thinking..." Stuck
- **Quota Exhausted**: Wait 24 hours for quota reset or upgrade to paid tier
- **Timeout**: The app now has a 30-second timeout with clear error messages

### ChromaDB Installation Issues
- If you encounter build errors, ensure you have Visual C++ Build Tools installed
- Or use the pre-built wheels with `chromadb>=0.4.22` (already in requirements.txt)

## Notes

- First processing of a PDF takes 2-5 minutes (embedding generation)
- Subsequent runs are instant (loads from persistent vector database)
- Chat history is maintained for the last 10 messages
- You can upload multiple PDFs and chat with all of them simultaneously
