# from fastapi import  UploadFile, HTTPException,  Request
# from langchain_community.document_loaders import PyPDFLoader
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain_chroma import Chroma
# from langchain.chains import create_history_aware_retriever, create_retrieval_chain, create_stuff_documents_chain
# from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
# from langchain_openai import ChatOpenAI, OpenAIEmbeddings
# import config

# embedding_function = OpenAIEmbeddings(openai_api_key=config.OPEN_AI_API_KEY)

# # Initialize text model
# llm = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0, api_key=config.OPEN_AI_API_KEY)


# class RetrievalChainManager:
#     def __init__(self):
#         self.rag_chain = None

#     def create_chain(self, file: UploadFile):
#         # Load text from the uploaded PDF file
#         loader = PyPDFLoader(file.filename)
#         text_splitter = RecursiveCharacterTextSplitter(
#             chunk_size=600,
#             chunk_overlap=60,
#             add_start_index=True,
#             separators=["\n\n", "\n", ".", " ", ""],
#         )
#         docs = loader.load_and_split(text_splitter=text_splitter)

#         # Store splits in the vector DB
#         retriever = Chroma.from_documents(docs, embedding_function, persist_directory=vector_db_path).as_retriever()

#         # Define chat history prompts
#         contextualize_q_system_prompt = """
#             Given a chat history and the latest user question which might reference context in the chat history,
#             formulate a standalone question which can be understood without the chat history.
#             Do NOT answer the question, just reformulate it if needed and otherwise return it as is.
#         """
#         contextualize_q_prompt = ChatPromptTemplate.from_messages(
#             [
#                 ("system", contextualize_q_system_prompt),
#                 MessagesPlaceholder("chat_history"),
#                 ("human", "{input}"),
#             ]
#         )

#         qa_system_prompt = """
#             You are an assistant for question-answering tasks.
#             Use the following pieces of retrieved context to answer the question.
#             If you don't know the answer, just say that you don't know.
#             Use three sentences maximum and keep the answer concise.
#             {context}
#         """
#         qa_prompt = ChatPromptTemplate.from_messages(
#             [
#                 ("system", qa_system_prompt),
#                 MessagesPlaceholder("chat_history"),
#                 ("human", "{input}"),
#             ]
#         )

#         # Create the retrieval chain
#         history_aware_retriever = create_history_aware_retriever(llm, retriever, contextualize_q_prompt)
#         question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)
#         self.rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

#     def get_rag_chain(self):
#         if self.rag_chain is None:
#             raise HTTPException(status_code=400, detail="No retrieval chain available. Please upload a file first.")
#         return self.rag_chain