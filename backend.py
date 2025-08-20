import os
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile
from langchain_community.document_loaders import TextLoader, PyPDFLoader, UnstructuredWordDocumentLoader
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from  langchain_community.chat_models import  ChatOpenAI
from langchain_openai import OpenAIEmbeddings
import logging
import tempfile
from langchain.docstore.document import Document

load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
app = FastAPI()
embeddings = OpenAIEmbeddings()

FAISS_INDEX_DIR = "faiss_index"

if os.path.exists(FAISS_INDEX_DIR):
    try:
        vector_store = FAISS.load_local(FAISS_INDEX_DIR, embeddings)
    except:
        logger.error("Failed to load existing FAISS index. Starting fresh.")
else:
    vector_store = None



@app.post("/upload-contract")
async def upload_contract(file: UploadFile):
    global vector_store
    
    tmp_file = tempfile.NamedTemporaryFile(delete=False)
    content = await file.read()
    tmp_file.write(content)
    tmp_file.close()
    
    if file.filename.endswith(".pdf"):
        loader = PyPDFLoader(tmp_file.name)
    elif file.filename.endswith(".docx"):
        loader = UnstructuredWordDocumentLoader(tmp_file.name)
    else:
        loader = TextLoader(tmp_file.name)
    
    docs = loader.load_and_split()
    embeddings = OpenAIEmbeddings()
    vector_store = FAISS.from_documents(docs, embeddings)
    
    return {"status": f"{file.filename} uploaded and processed."}


@app.get("/query-contract")
def query_contract(q: str):
    if vector_store is None:
        return {"error": "No report uploaded."}
    
    retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k":3})
    qa = RetrievalQA.from_chain_type(
        llm=ChatOpenAI(temperature=0),
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True
    )
    result = qa(q)
    # result: {"result": answer, "source_documents": [docs]}
    answer = result['result']
    sources = [{"page": getattr(doc.metadata, "page", None), "text": doc.page_content} for doc in result['source_documents']]
    
    return {"query": q, "answer": answer, "sources": sources}