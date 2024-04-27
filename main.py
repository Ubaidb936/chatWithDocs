from fastapi import FastAPI, UploadFile, File
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Create an instance of the FastAPI class
app = FastAPI()


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    
    with open(file.filename, "wb") as buffer:
        buffer.write(await file.read())
    
    loader = PyPDFLoader(file.filename)
    
    ##splitting the text file
    text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=600,  
            chunk_overlap=60,
            add_start_index=True,
            separators=["\n\n", "\n", ".", " ", ""],
        )
    
    langchain_docs = loader.load_and_split(text_splitter=text_splitter) 
    
    
        
        
    return {"contents":  langchain_docs[0]}