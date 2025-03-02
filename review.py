import os
import faiss
import ollama
from langchain.embeddings import OllamaEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS

DATA_DIR = "data/"
VECTOR_DB_PATH = "embeddings/code_index"

# Automatically detect code files based on extensions
def get_supported_code_files():
    """Returns a list of all code files in the data directory (any programming language)."""
    code_files = []
    for root, _, files in os.walk(DATA_DIR):
        for file in files:
            if file.count(".") == 1:  # Likely a code file (e.g., "script.py", "main.java")
                code_files.append(os.path.join(root, file))
    return code_files

# Step 1: Indexing Code Repository (Handles Any Language)
def index_code_repository():
    """Scans 'data/' folder, extracts code from all files, and indexes it."""
    embeddings = OllamaEmbeddings(model="llama3.2")
    texts = []
    
    code_files = get_supported_code_files()
    
    if not code_files:
        print("No code files found to index.")
        return []

    for file_path in code_files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                texts.append(f.read())
        except Exception as e:
            print(f"Skipping {file_path} due to error: {e}")

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    docs = text_splitter.create_documents(texts)

    vector_store = FAISS.from_documents(docs, embeddings)
    vector_store.save_local(VECTOR_DB_PATH)
    print(f"Indexed {len(code_files)} code files successfully!")
    return code_files

# Step 2: Retrieve Similar Code Snippets
def retrieve_similar_code(query, top_k=3):
    """Finds similar code snippets from the vector database."""
    embeddings = OllamaEmbeddings(model="llama3.2")
    try:
        vector_store = FAISS.load_local(VECTOR_DB_PATH, embeddings)
        results = vector_store.similarity_search(query, k=top_k)
        return [doc.page_content for doc in results]
    except Exception as e:
        print(f"Error loading vector database: {e}")
        return []

# Step 3: AI-Powered Code Review
def review_code(submitted_code, context):
    """Uses LLaMA 3.2 via Ollama to review submitted code."""
    prompt = f"""
    You are an expert code reviewer supporting multiple languages. Analyze the following code snippet 
    and provide insights, including:
    - Possible bugs or inefficiencies
    - Suggested refactoring steps
    - Best practices based on similar code in the knowledge base
    - Security vulnerabilities (if any)

    Submitted Code:
    {submitted_code}

    Context (Similar Code Found):
    {context}
    """
    
    response = ollama.chat(model="llama3.2", messages=[{"role": "user", "content": prompt}])
    return response["message"]["content"]

# Main Execution
if __name__ == "__main__":
    # Index all code files in the data folder
    code_files = index_code_repository()
    
    if not code_files:
        exit("No code files to process.")

    # Process each code file
    for file_path in code_files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                code_content = f.read()
        except Exception as e:
            print(f"Could not read {file_path}: {e}")
            continue

        # Retrieve similar code snippets for context
        similar_code = retrieve_similar_code(code_content)
        # Get the review from the AI-powered agent
        review_result = review_code(code_content, similar_code)
        
        print(f"\n### Code Review Report for {file_path} ###\n")
        print(review_result)
