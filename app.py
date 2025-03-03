import os
import faiss
import ollama
import requests
from flask import Flask, request, jsonify
from langchain_ollama import OllamaEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS

app = Flask(__name__)

DATA_DIR = "data/"  # Existing files directory
UPLOADS_DIR = "uploads/"  # New uploaded files
VECTOR_DB_PATH = "embeddings/code_index"
GITHUB_API_URL = "https://api.github.com/search/code"
GITHUB_ACCESS_TOKEN = "your_github_token"  # Replace with a valid token

# Ensure directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(UPLOADS_DIR, exist_ok=True)

# Function to process code files
def process_code(file_path):
    """Reads the file and returns the content."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {e}"

# Function to get all existing files from DATA_DIR
def get_existing_code_files():
    """Loads and returns all code files in the data directory."""
    code_files = []
    for root, _, files in os.walk(DATA_DIR):
        for file in files:
            file_path = os.path.join(root, file)
            code_files.append(file_path)
    return code_files

# Step 1: Index existing code repository
def index_code_repository():
    embeddings = OllamaEmbeddings(model="llama3.2")
    texts = []
    code_files = get_existing_code_files()

    if not code_files:
        print("No existing code files found.")
        return

    for file_path in code_files:
        code_content = process_code(file_path)
        texts.append(code_content)

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    docs = text_splitter.create_documents(texts)

    vector_store = FAISS.from_documents(docs, embeddings)
    vector_store.save_local(VECTOR_DB_PATH)
    print(f"Indexed {len(code_files)} existing code files.")

# Step 2: Retrieve Similar Code Snippets
def retrieve_similar_code(query, top_k=3):
    """First searches local indexed data, then falls back to the GitHub API if no match is found."""
    embeddings = OllamaEmbeddings(model="llama3.2")

    # Try loading local FAISS vector store
    try:
        vector_store = FAISS.load_local(VECTOR_DB_PATH, embeddings, allow_dangerous_deserialization=True)
        results = vector_store.similarity_search(query, k=top_k)
        if results:
            return [doc.page_content for doc in results]
    except Exception as e:
        print(f"Error loading FAISS: {e}")

    print("No similar code found locally. Querying external code search API...")
    return search_code_api(query)

# Step 3: External Code Search API
def search_code_api(query, top_k=3):
    """Searches GitHub API for relevant code snippets."""
    headers = {"Authorization": f"token {GITHUB_ACCESS_TOKEN}"}
    params = {"q": f"{query} in:file", "sort": "indexed", "order": "desc", "per_page": top_k}

    try:
        response = requests.get(GITHUB_API_URL, headers=headers, params=params)
        response.raise_for_status()
        results = response.json().get("items", [])
        return [f"// Code snippet from GitHub: {item.get('html_url', 'URL not found')}" for item in results] if results else ["// No relevant code found"]
    except requests.exceptions.RequestException as e:
        print(f"Error querying GitHub API: {e}")
        return ["// Error retrieving code from API"]

# Step 4: AI-Powered Code Review
def review_code(submitted_code, context):
    """Runs AI-powered review on submitted code."""
    prompt = f"""
    You are an expert code reviewer supporting multiple languages. Analyze the following code snippet:
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

# API Endpoint to Upload Code File
@app.route("/upload", methods=["POST"])
def upload_file():
    """Handles file uploads and runs a code review."""
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    file_path = os.path.join(UPLOADS_DIR, file.filename)
    file.save(file_path)

    # Process the uploaded code file
    code_content = process_code(file_path)
    similar_code = retrieve_similar_code(code_content)
    review_result = review_code(code_content, similar_code)

    return jsonify({"filename": file.filename, "review": review_result})

if __name__ == "__main__":
    index_code_repository()  # Index existing files at startup
    app.run(debug=True)
