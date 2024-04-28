from fastapi import FastAPI, UploadFile, File
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings.sentence_transformer import (
    SentenceTransformerEmbeddings,
)
from langchain_chroma import Chroma

# Create an instance of the FastAPI class
app = FastAPI()

# create the open-source embedding function
embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    
    with open(file.filename, "wb") as buffer:
        buffer.write(await file.read())
    
    loader = PyPDFLoader(file.filename)
    
    #splitting the text file
    text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=600,  
            chunk_overlap=60,
            add_start_index=True,
            separators=["\n\n", "\n", ".", " ", ""],
        )
    
    docs = loader.load_and_split(text_splitter=text_splitter) 
    
    db = Chroma.from_documents(docs, embedding_function, persist_directory="./chroma_db")
    
    docs = db.similarity_search("Who is Ubaid")    
    
    return {"contents":  docs[0].page_content}