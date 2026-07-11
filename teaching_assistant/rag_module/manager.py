import streamlit as st
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
import os

# Cấu hình Embedding model (Sử dụng Google Gemini Embedding)
def get_embedding_model():
    # Lưu ý: Thay API_KEY bằng biến môi trường hoặc input của giáo viên
    return GoogleGenerativeAIEmbeddings(model="models/embedding-001")

def process_and_vectorize(file_path):
    # 1. Đọc tài liệu
    if file_path.endswith('.pdf'):
        loader = PyPDFLoader(file_path)
    elif file_path.endswith('.docx'):
        loader = Docx2txtLoader(file_path)
    else:
        return None
    
    documents = loader.load()
    
    # 2. Băm văn bản (Chunking)
    # Chia nhỏ văn bản thành các đoạn 1000 ký tự, overlap 200 ký tự để giữ ngữ cảnh
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    texts = text_splitter.split_documents(documents)
    
    # 3. Nhúng Vector (Embedding) và lưu vào ChromaDB
    # Lưu tại thư mục tạm để truy vấn nhanh
    vectorstore = Chroma.from_documents(
        documents=texts, 
        embedding=get_embedding_model(),
        persist_directory="./rag_db" 
    )
    return vectorstore

def query_rag(vectorstore, question):
    # Tìm kiếm tài liệu liên quan
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    docs = retriever.get_relevant_documents(question)
    
    # Ghép nội dung để gửi cho AI
    context = "\n".join([d.page_content for d in docs])
    return context
