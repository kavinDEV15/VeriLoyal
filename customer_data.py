from pymongo import MongoClient
from nomic import embed
import chromadb
from config import MONGO_URI, DATABASE_NAME, CUSTOMER_COLLECTION, CHROMA_DB_PATH

# Initialize MongoDB Client
mongo_client = MongoClient(MONGO_URI)
db = mongo_client[DATABASE_NAME]
customer_collection = db[CUSTOMER_COLLECTION]

# Initialize ChromaDB for fast retrieval
client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
collection = client.get_or_create_collection(name="customer_data")

# Fetch Customer Data from MongoDB
def get_customer_info(phone):
    user = customer_collection.find_one({"phone": phone})
    if not user:
        return None
    return user

# Generate and Store Embeddings
def generate_embeddings():
    for user in customer_collection.find():
        phone = user["phone"]
        context = f"""
        Customer Name: {user.get('name', 'Unknown')}
        Plan: {user.get('plan', {}).get('name', 'N/A')}
        Balance: {user.get('balance', 'N/A')}
        Data Remaining: {user.get('data_remaining', 'N/A')} GB
        Recharge History: {user.get('recharge_history', [])}
        """
        embedding = embed([context])[0]
        collection.add(
            ids=[phone], embeddings=[embedding], metadatas=[{"phone": phone}]
        )

# Retrieve User Context from ChromaDB
def retrieve_user_context(phone):
    query_text = str(get_customer_info(phone))
    if not query_text:
        return "No specific customer data found."
    
    query_embedding = embed([query_text])[0]
    results = collection.query(
        query_embeddings=[query_embedding], n_results=1
    )
    if results["ids"]:
        return query_text
    return "No specific context found."
