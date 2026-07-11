import streamlit as st
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, RapidOCRLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma

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
    """
    Tải tài liệu dựa trên định dạng tệp, chia tách văn bản thành các chunks 
    và tiến hành vector hóa để lưu trữ vào Chroma vector store.
    """
    # Khởi tạo danh sách chứa tài liệu ban đầu
    documents = []
    
    # Xác định phần mở rộng của tệp tin để sử dụng loader phù hợp
    ext = os.path.splitext(file_path)[-1].lower()
    
    if ext == ".pdf":
        loader = PyPDFLoader(file_path)
        documents = loader.load()
    elif ext == ".docx":
        loader = Docx2txtLoader(file_path)
        documents = loader.load()
    elif ext in [".png", ".jpg", ".jpeg", ".tiff", ".bmp"]:
        loader = RapidOCRLoader(file_path)
        documents = loader.load()
    else:
        raise ValueError(f"Định dạng tệp '{ext}' không được hỗ trợ.")
        
    # Chia tách văn bản thành các phân đoạn nhỏ hơn (chunks)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, 
        chunk_overlap=200
    )
    splits = text_splitter.split_documents(documents)
    
    # Lấy mô hình nhúng Gemini
    embedding_model = get_embedding_model()
    
    # Vector hóa và lưu trữ vào cơ sở dữ liệu Chroma
    vectorstore = Chroma.from_documents(documents=splits, embedding=embedding_model)
    
    return vectorstore

def query_rag(vectorstore, question):
    """
    Tìm kiếm tài liệu liên quan bằng phương thức invoke mới và trả về danh sách tài liệu
    """
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    docs = retriever.invoke(question)
    return docs
