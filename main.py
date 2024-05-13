from fastapi import FastAPI, Request, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI
from langchain.chains import create_history_aware_retriever
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.messages import HumanMessage
from fastapi.middleware.cors import CORSMiddleware
import os
import config    
import shutil
import pdb
import time


# path where the vector db is stored
vector_db_path = "./chroma_db"


# initialize the embedding model
embedding_function = OpenAIEmbeddings(openai_api_key = config.OPEN_AI_API_KEY)

# initialize the text llm
llm = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0, api_key = config.OPEN_AI_API_KEY)


# Global variable to store rag_chain
rag_chain = None

# stores the chat history
chat_history = []


# Create an instance of the FastAPI class
app = FastAPI()



# app.mount("/static", StaticFiles(directory="gui/build/static"), name="static")

app.add_middleware( CORSMiddleware, 
                    allow_origins=["*"],
                    allow_credentials=True, 
                    allow_methods=["*"], 
                    allow_headers=["*"], 
                    )


def create_chain(file: UploadFile):
    
    #loading text and splitting the text
    loader = PyPDFLoader(file.filename)
    text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=600,  
            chunk_overlap=60,
            add_start_index=True,
            separators=["\n\n", "\n", ".", " ", ""],
    )
    docs = loader.load_and_split(text_splitter=text_splitter) 
    
    # storing the splits on the vector DB....
    
    
    db = Chroma.from_documents(docs, embedding_function, persist_directory=vector_db_path)
    
    # db._client.reset
            
        
    
    
    retriever = db.as_retriever()
    
    
    contextualize_q_system_prompt = """Given a chat history and the latest user question \
            which might reference context in the chat history, formulate a standalone question \
            which can be understood without the chat history. Do NOT answer the question, \
            just reformulate it if needed and otherwise return it as is."""
            
    contextualize_q_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", contextualize_q_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
    )
    
    history_aware_retriever = create_history_aware_retriever(
        llm, retriever, contextualize_q_prompt
    )
    
    qa_system_prompt = """You are an assistant for question-answering tasks. \
        Use the following pieces of retrieved context to answer the question. \
        If you don't know the answer, just say that you don't know. \
        Use three sentences maximum and keep the answer concise.\
        {context}"""
    qa_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", qa_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )


    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)

    
    
    return create_retrieval_chain(history_aware_retriever, question_answer_chain)


## Upload the file to the vector db
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    
    
    global rag_chain
    
    # checking the extension of the file (only .pdf files are allowed)
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

    # storing the file locally
    with open(file.filename, "wb") as buffer:
        buffer.write(await file.read())
    
    rag_chain = create_chain(file) 

    
    return {"message":  "File is upload successfully"}

@app.get("/search")
async def search(query: str):
    
    global rag_chain
    
    if rag_chain is None:
        return "Please upload the file first."

    ai_msgs = rag_chain.invoke({"input": query, "chat_history": chat_history})
    chat_history.extend([HumanMessage(content=query), ai_msgs["answer"]])
    
    return ai_msgs["answer"]


@app.get("/reset")
async def reset():
    
    global rag_chain
    
    
    rag_chain = None
    
    
    db = Chroma(persist_directory=vector_db_path, embedding_function=embedding_function)
    
    db._client.
    
    
    return {"message": "all the"}
    
    
    
    
    
    
    
    


# @app.get("/")
# async def read_index(request: Request) -> HTMLResponse:
#     with open("gui/build/index.html", "r") as f:
#         html_content = f.read()
#     return HTMLResponse(content=html_content, status_code=200)



    
