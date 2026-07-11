import streamlit as st
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def backup_to_googlesheet(data_dict):
    """
    Gửi thông tin giao tiếp về Google Sheet bằng tài khoản bảo mật từ Secrets
    """
    try:
        # Lấy thông tin xác thực từ Streamlit Secrets
        google_creds = dict(st.secrets["gcp_service_account"])
        
        # Đăng nhập qua gspread
        client = gspread.service_account_from_dict(google_creds)
        
        # Mở bảng tính và ghi dữ liệu
        sheet = client.open("Data_Nhat_Ky_Giang_Day").sheet1
        sheet.append_row([data_dict['timestamp'], data_dict['query'], data_dict['response']])
    except Exception as e:
        st.error(f"Lỗi khi sao lưu dữ liệu lên Google Sheets: {e}")

def get_embedding_model():
    """
    api_key = st.secrets["GEMINI_API_KEY"]
    return GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=api_key)

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
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    texts = text_splitter.split_documents(documents)
    
    # 3. Nhúng Vector (Embedding) và lưu vào ChromaDB
    vectorstore = Chroma.from_documents(
        documents=texts, 
        embedding=get_embedding_model(),
        persist_directory="./rag_db" 
    )
    return vectorstore

def query_rag(vectorstore, question):
    # Tìm kiếm tài liệu liên quan
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    docs = retriever.invoke(question)  # <-- Thay đổi tại đây

    # Ghép nội dung để gửi cho AI
    context = "\n".join([d.page_content for d in docs])
    return context


