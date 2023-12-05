import uuid
import chromadb
import tiktoken
from chromadb.config import Settings 
import os 
from mongo import * 
from langchain.text_splitter import RecursiveCharacterTextSplitter
import re 

print(collection.count_documents({}))

load_dotenv()


chromadb_ip = os.environ["CHROMA_DB_IP"]
chromadb_port = os.environ["CHROMA_DB_PORT"]
client = chromadb.HttpClient(settings=Settings(allow_reset=True), host=chromadb_ip, port=chromadb_port)


# delete nice_cks collection if it exists

client.delete_collection("nice_cks")
print("deleted collection nice_cks if it exists")

vector_collection = client.get_or_create_collection("nice_cks")
cursor = collection.find({})
count = 0 
for document in cursor:
    print(document["url"])
    count += 1

print(count)

def remove_markdown_links(text):
    # Pattern to match Markdown links
    pattern = r'\[([^]]+)]\(([^)"]+)(?: \"[^\"]+\")?\)'

    # Substitute matches with an empty string
    return re.sub(pattern, '', text)

def token_counter(s): 
    encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
    num_tokens = len(encoding.encode(s))
    return num_tokens

def split_text(s, chunk_size, chunk_overlap):
    print("splitting text")
    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    return text_splitter.split_text(s)


def col_to_vec(collection, vector_collection):
    all_ids = collection.find({}, {"_id": 1})
    all_ids = list(all_ids)
    print(len(all_ids))
    print(count == len(all_ids))
    for id in all_ids:
        url = collection.find_one({"_id": id["_id"]})["url"]
        content = collection.find_one({"_id": id["_id"]})["content"]
        content = remove_markdown_links(content)
        title = collection.find_one({"_id": id["_id"]})["title"]
        chunks = split_text(content, 350, 30)
        for chunk in chunks: 
            # add title to chunk 
            chunk = "# " + title + "\n" + chunk
            # add data to chromadb
            vector_collection.add(
                ids=[str(uuid.uuid1())],
                documents=[chunk],
                metadatas=[{"url": url}], 
            ) 
            print(f"added {title} chunk to chromadb")
            # print(chunk)
            print("url: " + url)
            print("length: ", token_counter(chunk), "tokens", len(chunk), "characters")
            print("--------------------------------------------------")



col_to_vec(collection, vector_collection)