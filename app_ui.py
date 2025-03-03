import streamlit as st
import requests

# Flask API Endpoint
API_URL = "http://127.0.0.1:5000/upload"

st.title("AI-Powered Code Review")
st.write("Upload your code file to receive an AI-powered review.")

# File uploader
uploaded_file = st.file_uploader("Choose a code file", type=["py", "java", "cpp", "js", "ts", "go", "cs"])

if uploaded_file is not None:
    st.write("Uploading file...")

    # Send the file to Flask API
    files = {"file": uploaded_file.getvalue()}
    response = requests.post(API_URL, files=files)

    if response.status_code == 200:
        result = response.json()
        st.success(f"Code Review Report for {result['filename']}:")
        st.text_area("Review", result["review"], height=300)
    else:
        st.error(f"Error: {response.json().get('error', 'Unknown error')}")
