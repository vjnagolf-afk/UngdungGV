import streamlit as st
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
# Bổ sung Loader chuyên dụng cho tệp ảnh
from langchain_community.document_loaders.image import RapidOCRBlobLoader
from langchain_core.documents import Document
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
    
    # 1. Đọc tài liệu đa định dạng (PDF, DOCX, ẢNH)
    if file_path.endswith('.pdf'):
        loader = PyPDFLoader(file_path, extract_images=True)
        documents = loader.load()
    elif file_path.endswith('.docx'):
        loader = Docx2txtLoader(file_path)
        documents = loader.load()
    elif file_path.endswith(('.png', '.jpg', '.jpeg')):
        # Xử lý OCR trực tiếp từ file ảnh chụp bài giảng
        try:
            with open(file_path, "rb") as f:
                blob_content = f.read()
            # Khởi tạo bộ OCR trích xuất chữ từ ảnh
            ocr_loader = RapidOCRBlobLoader()
            # Tạo một document giả lập chứa text từ OCR
            ocr_results = ocr_loader.load_embedding_from_blob(blob_content) if hasattr(ocr_loader, 'load_embedding_from_blob') else []
            
            # Giải pháp đọc ảnh tiêu chuẩn nếu hàm blob không tương thích phiên bản
            if not ocr_results:
                from langchain_community.document_loaders import RapidOCRLoader
                loader = RapidOCRLoader(file_path)
                documents = loader.load()
        except Exception as ocr_err:
            raise ValueError(f"Không thể trích xuất chữ từ file ảnh này: {str(ocr_err)}")
    else:
        return None
    
    # 2. Băm văn bản (Chunking)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    texts = text_splitter.split_documents(documents)
    
    # Kiểm tra an toàn để tránh lỗi trống dữ liệu vector của ChromaDB
    if not texts or len(texts) == 0:
        raise ValueError("Tài liệu không chứa dữ liệu văn bản hoặc cấu trúc file không cho phép trích xuất chữ.")
    
    # 3. Nhúng Vector (Embedding) và lưu vào ChromaDB
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
    
    # Ghép nội dung để gửi cho AI
    context = "\n".join([d.page_content for d in docs])
    return context
