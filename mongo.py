from dotenv import load_dotenv
import pymongo
import os

load_dotenv()

DB_ADDR = os.getenv("DB_ADDR")
DB_USER = os.getenv("DB_USER")
DB_PW = os.getenv("DB_PW")


# Connect to MongoDB
client = pymongo.MongoClient(DB_ADDR, username=DB_USER, password=DB_PW)
# Create database, web_scraping, and collection, nice_cks
db = client.web_scraping
collection = db.nice_cks

# index 
# a = collection.create_index([("title", pymongo.TEXT)])
# print(a)

def insert_data(title, url, content):
    # Insert data into MongoDB
    data = {
        "title": title,
        "url": url,
        "content": content
    }
    collection.insert_one(data)
    print(f"Inserted data for {title} into MongoDB")