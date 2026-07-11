import streamlit as st
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, RapidOCRLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def backup_to_googlesheet(data_dict, google_creds):
    """
    Gửi thông tin giao tiếp về Google Sheet bằng tài khoản dịch vụ
    """
    try:
        client = gspread.service_account_from_dict(google_creds)
        sheet = client.open("Data_Nhat_Ky_Giang_Day").sheet1
        sheet.append_row([data_dict['timestamp'], data_dict['query'], data_dict['response']])
        return True
    except Exception as e:
        st.error(f"Lỗi khi sao lưu dữ liệu lên hệ thống Cloud: {e}")
        return False

def get_embedding_model():
    """
    Cấu hình Embedding model sử dụng mô hình Gemini chính xác
    """
    return GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

def process_and_vectorize(file_path):
    documents = []
    
    # 1. Trích xuất tài liệu đa định dạng (PDF, DOCX, ẢNH) dựa trên đuôi file
    ext = os.path.splitext(file_path).lower()
    
    try:
        if ext == '.pdf':
            loader = PyPDFLoader(file_path, extract_images=True)
            documents = loader.load()
        elif ext == '.docx':
            loader = Docx2txtLoader(file_path)
            documents = loader.load()
        elif ext in ['.png', '.jpg', '.jpeg']:
            # SỬA LỖI: Gọi trực tiếp bộ OCR tiêu chuẩn đã được import ở dòng số 3
            loader = RapidOCRLoader(file_path)
            documents = loader.load()
        else:
            return None
            
    except Exception as read_err:
        raise ValueError(f"Lỗi hệ thống khi trích xuất dữ liệu tài liệu: {str(read_err)}")
    
    # 2. Băm văn bản thành các đoạn nhỏ (Chunking)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    texts = text_splitter.split_documents(documents)
    
    # Kiểm tra an toàn để tránh lỗi truyền mảng rỗng [] vào cơ sở dữ liệu vector
    if not texts or len(texts) == 0:
        raise ValueError("Tài liệu không chứa nội dung văn bản hoặc hệ thống OCR không trích xuất được chữ từ hình ảnh.")
    
    # 3. Nhúng dữ liệu (Embedding) và lưu giữ tạm vào ChromaDB
    vectorstore = Chroma.from_documents(
        documents=texts, 
        embedding=get_embedding_model(),
        persist_directory="./rag_db" 
    )
    return vectorstore

def query_rag(vectorstore, question):
    # Tìm kiếm tài liệu liên quan bằng phương thức invoke mới
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    docs = retriever.invoke(question)
    
    # Ghép nội dung ngữ cảnh tìm được để bàn giao cho mô hình AI
    context = "\n".join([d.page_content for d in docs])
    return context
