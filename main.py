from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings.sentence_transformer import (
    SentenceTransformerEmbeddings,
)
from langchain_chroma import Chroma
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from fastapi.middleware.cors import CORSMiddleware
import os
import config



# Create an instance of the FastAPI class
app = FastAPI()


app.mount("/static", StaticFiles(directory="gui/build/static"), name="static")

app.add_middleware( CORSMiddleware, 
                    allow_origins=["*"],
                    allow_credentials=True, 
                    allow_methods=["*"], 
                    allow_headers=["*"], 
                    )


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
    #if db existed then add new file to db otherwiese create new add.
    
    return {"message":  "File is upload successfully"}



@app.get("/search")
async def search(query: str):
    db = Chroma(persist_directory="./chroma_db", embedding_function=embedding_function).as_retriever()
    
    #create a llm chain first
    llm = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0, api_key = config.OPEN_AI_API_KEY)
    
    prompt_template = """Use the following pieces of context to answer the question at the end. 
    If you don't know the answer, just say that you don't know, don't try to make up an answer.
    Use three sentences maximum. Keep the answer as concise as possible. 
    Always say "thanks for asking!" at the end of the answer.
    {context}
    Question: {question}
    Helpful Answer:"""
    
    prompt = PromptTemplate(
    input_variables=["context", "question"],
    template=prompt_template,
    )
    llm_chain = prompt | llm | StrOutputParser()
    
    rag_chain = ({"context": db, "question": RunnablePassthrough()}| llm_chain)
    
    ans = rag_chain.invoke(query)
    
    return ans  


@app.get("/")
async def read_index(request: Request) -> HTMLResponse:
    with open("gui/build/index.html", "r") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content, status_code=200)



    
