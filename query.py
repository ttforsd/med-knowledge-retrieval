import chromadb
from chromadb.config import Settings 
from dotenv import load_dotenv
import os 
from llamaapi import LlamaAPI
from langchain_experimental.llms import ChatLlamaAPI
from langchain.schema import StrOutputParser
from langchain.vectorstores.chroma import Chroma
from langchain.schema.runnable import RunnablePassthrough
from langchain.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI


embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

load_dotenv()

# choose language model
llama_key = os.environ["LLAMA_API_KEY"]
llama = LlamaAPI(llama_key)
llm = ChatLlamaAPI(client=llama, temperature=0.1)
llm = ChatOpenAI(temperature=0.1)

load_dotenv()
chromadb_ip = os.environ["CHROMA_DB_IP"]
chromadb_port = os.environ["CHROMA_DB_PORT"]

template = """Use the following pieces of context to answer the question at the end. 
If you don't know the answer, just say that you don't know, don't try to make up an answer. 
Do not use any other sources of information to answer the question.
Include all the details in your answer.
Answer in bullet points.
{context}
Question: {question}
Answer:"""

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

prompt = PromptTemplate.from_template(template)

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


while True: 
    print()
    query = input("enter query: ")
    send_query("nice_cks", query)