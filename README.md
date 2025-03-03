# Code_Review

# Folder Structure
📂 project-root/
│── 📂 data/          # Contains existing code files (indexed at startup)
│── 📂 embeddings/    # Stores FAISS vector database for local code retrieval
│── 📂 uploads/       # Stores newly uploaded code files
│── 📜 app.py         # Flask backend for uploading and reviewing code
│── 📜 app_ui.py      # Streamlit-based frontend for the app (if applicable)
│── 📜 README.md      # Project documentation

# Key Components
1️⃣ data/ (Local Code Repository)
    -> Stores existing code files that are indexed at startup.
    -> Helps find similar code snippets before calling the GitHub API.

2️⃣ embeddings/ (Vector Database)
    -> Contains FAISS embeddings for fast local code similarity search.
    -> Auto-updated when new files are indexed.

3️⃣ uploads/ (New Code Submissions)
    -> Stores uploaded code files via the Flask API.
    -> These files are processed, vectorized, and reviewed using AI.

4️⃣ app.py (Flask Backend)
    -> Provides REST API endpoints to upload and analyze code.
    -> Uses FAISS & GitHub API for retrieving similar code.
    -> Calls Ollama AI for code review and improvement suggestions.

5️⃣ app_ui.py (Streamlit Frontend)
    -> (Optional) Provides a web UI to upload and review code.
    -> Displays AI-generated insights about uploaded files.

# Ollama
-> From this website download ollama setup https://ollama.com/
-> install the app after the installation you will get an ollama terminal where you need to run:-
    ollama run llama3.2
    # this will install llama3.2 model in your system

# Setup
1) clone the repo:-
git clone "ssh-link"
cd Code_Review

2) create virtual env:-
python -m venv ".venv"

3) activate the virtual env:-
.\.venv\Scripts\activate

4) install all the required packages:-
python install -r requirements.txt

5) To run the server:-
python app.py

6) To run the ui:-
streamlit run app_ui.py