import streamlit as st
import requests
from settings import BACKEND_URL
st.title("AI Contract Query Demo")

uploaded_file = st.file_uploader("Upload contract template (PDF/TXT)", type=["pdf","txt"])
if uploaded_file:
    response = requests.post(f"{BACKEND_URL}", files={"file": uploaded_file})
    st.write(response.json())

query = st.text_input("Ask a question about the contract:")
if st.button("Submit Query"):
    response = requests.get(f"{BACKEND_URL}/query-contract?q={query}")
    data = response.json()
    if "answer" in data:
        st.subheader("Answer")
        st.write(data["answer"])
        st.subheader("Source Snippets")
        for src in data["sources"]:
            st.write(src["text"])
