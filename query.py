__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
import chromadb
from chromadb.config import Settings 
from dotenv import load_dotenv
import os 
from llamaapi import LlamaAPI
# from langchain import ChatLlamaAPI
from langchain.schema import StrOutputParser
from langchain.vectorstores.chroma import Chroma
from langchain.schema.runnable import RunnablePassthrough
from langchain.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain_google_genai import GoogleGenerativeAI
import requests



embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

load_dotenv(override=True)

# pass network traffic through the proxy
proxy = os.environ["PROXY_ADDR"]
os.environ['http_proxy'] = proxy 
os.environ['HTTP_PROXY'] = proxy
os.environ['https_proxy'] = proxy
os.environ['HTTPS_PROXY'] = proxy

# test the proxy (get ip from ifconfig.me)
print("current ip:", requests.get("https://ifconfig.me").text)

# choose language model
llama_key = os.environ["LLAMA_API_KEY"]
llama = LlamaAPI(llama_key)
# llm = ChatLlamaAPI(client=llama, temperature=0.1)
# llm = ChatOpenAI(temperature=0.1)
google_key = os.environ["GOOGLE_API_KEY"]
llm = GoogleGenerativeAI(model="gemini-1.0-pro", api_key=google_key, temperature=0.1)

chromadb_ip = os.environ["CHROMA_DB_IP"]
chromadb_port = os.environ["CHROMA_DB_PORT"]

template = """Use the following pieces of context to answer the question at the end. 
The target audience for the answer is a healthcare professional.
Include drug names and procedures where applicable in the answer.
If you don't know the answer, just say that you don't know, don't try to make up an answer. 
Do not use any other sources of information to answer the question.
Answer need to be comprehensive and detailed, yet easy to read.
Answer in easy to read MD bullet point format.
{context}
Question: {question}
Answer:"""

# template = """User: Use the following pieces of context to answer the question at the end. 
# If you don't know the answer, just say that you don't know, don't try to make up an answer. 
# Do not use any other sources of information to answer the question.
# Include all the details in your answer.
# Answer in bullet points.
# {context}
# Question: {question}
# Answer:"""

llama_template = """[INST]<<SYS>>
You are a helpful, respectful and honest assistant. Go straight into the answering the question, no extra texts before the answer. Always answer as helpfully as possible using the context text provided. Your answers should only answer the question once and not have any text after the answer is done.\n\nIf a question does not make any sense, or is not factually coherent, explain why instead of answering something not correct. If you don't know the answer to a question, please don't share false information. \n<</SYS>>
Use the following pieces of context to answer the question at the end. 
If you don't know the answer, just say that you don't know, don't try to make up an answer. 
Do not use any other sources of information to answer the question.
Include names of medications and procedures in the answer.
Include all the details in your answer.
Answer in bullet points.
{context}
Question: {question}
[/INST]"""


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

# for openai template
prompt = PromptTemplate.from_template(template)

# # use llama template
# prompt = PromptTemplate.from_template(llama_template)

print(prompt)

client = chromadb.HttpClient(settings=Settings(allow_reset=True), host=chromadb_ip, port=chromadb_port)

def send_query(collection_name, query):
    # connet to client 
    client = chromadb.HttpClient(settings=Settings(allow_reset=True), host=chromadb_ip, port=chromadb_port)
    db = Chroma(
        client=client,
        collection_name=collection_name,
        embedding_function=embedding_function
    )
    retriever = db.as_retriever(search_type="similarity", search_kwargs={"k": 6})
    results = retriever.get_relevant_documents(query)
    print(results)
    urls = set()
    for result in results:
        urls.add(result.metadata["url"])
    print("links used to answer question: ")
    for url in urls:
        print(url)
    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    print("answer: ")
    response = rag_chain.invoke(query)
    print(response)
    return urls, response

if __name__ == "__main__":
    while True: 
        print()
        client = chromadb.HttpClient(settings=Settings(allow_reset=True), host=chromadb_ip, port=chromadb_port)
        query = input("enter query: ")
        send_query("nice_cks", query)