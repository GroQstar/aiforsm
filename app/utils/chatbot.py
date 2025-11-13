import streamlit as st
import os
from collections import defaultdict
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import AIMessage, HumanMessage
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from dotenv import load_dotenv

def get_context_retriever_chain(vectordb):
    """
    Create a context retriever chain for generating responses based on the chat history and vector database

    Parameters:
    - vectordb: Vector database used for context retrieval

    Returns:
    - retrieval_chain: Context retriever chain for generating responses
    """
    # Load environment variables (gets api keys for the models)
    # Load .env from project root
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    env_path = os.path.join(project_root, '.env')
    load_dotenv(dotenv_path=env_path)
    # Also try loading from current directory as fallback
    load_dotenv()
    # Get API key from environment
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found in environment. Please add it to your .env file.")
    # Initialize the model, set the retreiver and prompt for the chatbot
    # Use gemini-2.5-flash (latest, faster model)
    # gemini-pro is deprecated - use gemini-2.5-flash or gemini-1.5-pro
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.2, convert_system_message_to_human=True, google_api_key=api_key)
    # Use retriever with similarity search (works with our batch embedding)
    retriever = vectordb.as_retriever(search_kwargs={"k": 5})  # Get top 5 most similar chunks
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a chatbot. You'll receive a prompt that includes a chat history and retrieved content from the vectorDB based on the user's question. Your task is to respond to the user's question using the information from the vectordb, relying as little as possible on your own knowledge. If for some reason you don't know the answer for the question, or the question cannot be answered because there's no context, ask the user for more details. Do not invent an answer. Answer the questions from this context: {context}"),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}")
    ])
    # Create chain for generating responses and a retrieval chain
    chain = create_stuff_documents_chain(llm=llm, prompt=prompt)
    retrieval_chain = create_retrieval_chain(retriever, chain)
    return retrieval_chain

def get_response(question, chat_history, vectordb):
    """
    Generate a response to the user's question based on the chat history and vector database

    Parameters:
    - question (str): The user's question
    - chat_history (list): List of previous chat messages
    - vectordb: Vector database used for context retrieval

    Returns:
    - response: The generated response
    - context: The context associated with the response
    
    Raises:
    - Exception: If API call fails (quota, network, timeout, etc.)
    """
    import signal
    import threading
    
    try:
        chain = get_context_retriever_chain(vectordb)
        
        # Use timeout to prevent hanging (30 seconds max)
        result_container = {"response": None, "error": None, "timeout": False}
        
        def invoke_with_timeout():
            try:
                result_container["response"] = chain.invoke({"input": question, "chat_history": chat_history})
            except Exception as e:
                result_container["error"] = e
        
        # Run in a thread with timeout
        thread = threading.Thread(target=invoke_with_timeout)
        thread.daemon = True
        thread.start()
        thread.join(timeout=30.0)  # 30 second timeout
        
        if thread.is_alive():
            result_container["timeout"] = True
            raise Exception("Request timed out after 30 seconds. This usually means your quota is exhausted or the API is slow.")
        
        if result_container["error"]:
            raise result_container["error"]
        
        if result_container["response"]:
            return result_container["response"]["answer"], result_container["response"]["context"]
        else:
            raise Exception("No response received from API")
            
    except Exception as e:
        # Re-raise with more context
        error_msg = str(e)
        if "timeout" in error_msg.lower():
            raise Exception("⏱️ Request timed out. Your quota may be exhausted. Wait 24 hours or upgrade to paid tier.")
        raise Exception(f"Failed to generate response: {error_msg}")

def chat(chat_history, vectordb):
    """
    Handle the chat functionality of the application

    Parameters:
    - chat_history (list): List of previous chat messages
    - vectordb: Vector database used for context retrieval

    Returns:
    - chat_history: Updated chat history
    """
    user_query = st.chat_input("Ask a question:")
    if user_query is not None and user_query != "":
        # Add user message to history immediately (so it doesn't disappear)
        chat_history = chat_history + [HumanMessage(content=user_query)]
        
        # Try to generate response with error handling
        try:
            # Show spinner
            with st.spinner("🤔 Thinking... (max 30 seconds)"):
                # Generate response based on user's query, chat history and vectorstore
                response, context = get_response(user_query, chat_history[:-1], vectordb)  # Exclude just-added user message
            
            # Add AI response to history
            chat_history = chat_history + [AIMessage(content=response)]
            
            # Display source of the response on sidebar
            with st.sidebar:
                st.subheader("📚 Sources")
                metadata_dict = defaultdict(list)
                for metadata in [doc.metadata for doc in context]:
                    metadata_dict[metadata['source']].append(metadata['page'])
                for source, pages in metadata_dict.items():
                    st.write(f"**{source}**")
                    st.write(f"Pages: {', '.join(map(str, sorted(set(pages))))}")
                    
        except Exception as e:
            error_msg = str(e)
            
            # Check if it's a quota error
            if "quota" in error_msg.lower() or "429" in error_msg or "exceeded" in error_msg.lower() or "timeout" in error_msg.lower():
                error_response = """
                **🚫 Quota Limit Reached or Request Timed Out**
                
                Your free tier quota has been exceeded, or the request timed out. Chat generation also requires API calls.
                
                **Options:**
                1. **Wait 24 hours** for quota reset
                2. **Upgrade to paid tier** at https://ai.google.dev/pricing
                
                Your documents are already processed and ready - once quota resets, you can chat immediately!
                """
            else:
                error_response = f"**Error generating response:** {error_msg}"
            
            # Add error message to chat history
            chat_history = chat_history + [AIMessage(content=error_response)]
    
    # Display chat history (all previous messages) - this is the only place messages are displayed
    for message in chat_history:
        with st.chat_message("AI" if isinstance(message, AIMessage) else "Human"):
            if isinstance(message, AIMessage) and ("🚫" in message.content or "⏱️" in message.content):
                st.error(message.content)
            else:
                st.write(message.content)
    
    return chat_history