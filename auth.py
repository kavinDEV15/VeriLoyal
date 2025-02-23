import streamlit as st
from pymongo import MongoClient
import bcrypt
from config import MONGO_URI, DATABASE_NAME, USER_COLLECTION

# Initialize MongoDB Client
mongo_client = MongoClient(MONGO_URI)
db = mongo_client[DATABASE_NAME]
user_collection = db[USER_COLLECTION]

# Function to hash password
def hash_password(password):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt)

# Function to verify password
def verify_password(stored_hash, password):
    return bcrypt.checkpw(password.encode('utf-8'), stored_hash)

# User Authentication
def authenticate_user(phone, password):
    user = user_collection.find_one({"phone": phone})
    if user and user["password"] == password:  # Compare plaintext password
        return user
    return None

# Register New User
def register_user(phone, name, password):
    if user_collection.find_one({"phone": phone}):
        return False, "User already exists!"
    
    password_hash = hash_password(password).decode('utf-8')
    user_collection.insert_one({
        "phone": phone,
        "name": name,
        "password_hash": password_hash
    })
    return True, "User registered successfully!"

# Login UI
def login():
    st.sidebar.header("🔐 Login")
    phone = st.sidebar.text_input("Phone Number")
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        user = authenticate_user(phone, password)
        if user:
            st.session_state["authenticated"] = True
            st.session_state["user_phone"] = phone
            st.session_state["user_name"] = user["name"]
            st.sidebar.success(f"✅ Welcome {user['name']}!")
            st.rerun()
        else:
            st.sidebar.error("❌ Invalid credentials")
