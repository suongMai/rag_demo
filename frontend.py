import streamlit as st
import requests

st.title("AI Contract Query Demo")

uploaded_file = st.file_uploader("Upload contract template (PDF/TXT)", type=["pdf","txt"])
if uploaded_file:
    response = requests.post("http://localhost:8000/upload-contract", files={"file": uploaded_file})
    st.write(response.json())

query = st.text_input("Ask a question about the contract:")
if st.button("Submit Query"):
    response = requests.get(f"http://localhost:8000/query-contract?q={query}")
    data = response.json()
    if "answer" in data:
        st.subheader("Answer")
        st.write(data["answer"])
        st.subheader("Source Snippets")
        for src in data["sources"]:
            st.write(src["text"])
