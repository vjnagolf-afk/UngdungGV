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
        google_creds = dict(st.secrets["gcp_service_account"])
        client = gspread.service_account_from_dict(google_creds)
        sheet = client.open("Data_Nhat_Ky_Giang_Day").sheet1
        sheet.append_row([data_dict['timestamp'], data_dict['query'], data_dict['response']])
    except Exception as e:
        error_msg = str(e)
        # Nếu lỗi chứa "200" (tức là thao tác thành công nhưng bị hiểu nhầm), ta bỏ qua
        if "200" not in error_msg:
            st.error(f"Lỗi khi sao lưu dữ liệu lên Google Sheets: {error_msg}")
def get_embedding_model():
    api_key = st.secrets["GEMINI_API_KEY"]
    # Sử dụng chính xác tên mô hình embedding từ danh sách của thầy
    return GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-2", google_api_key=api_key)
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
    docs = retriever.invoke(question)  

    # Ghép nội dung để gửi cho AI
    context = "\n".join([d.page_content for d in docs])
    return context
