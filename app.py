import streamlit as st
import time
import random
import requests
import json
import plotly.graph_objects as go
import plotly.express as px
from auth import login
from customer_data import get_customer_info
from llm_handler import get_ai_response

# Check Authentication
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
    st.session_state["user_phone"] = None
    st.session_state["chat_open"] = False
    st.session_state["chat_history"] = []
    st.session_state["notifications"] = []

st.sidebar.info("👋 Hi, valuable user! Welcome to Verizon's customer portal. Enjoy seamless connectivity, exclusive offers, and personalized support!")
login()

if not st.session_state["authenticated"]:
    st.stop()

# Fetch customer data from MongoDB
phone = st.session_state["user_phone"]
user_data = get_customer_info(phone)

if not user_data:
    st.error("User data not found!")
    st.stop()

st.title(f"Welcome, {st.session_state['user_name']}! 🎉")

col1, col2 = st.columns(2)
with col1:
    st.info("📞 **Mobile Plan**")
    st.write(f"**Plan:** {user_data['plan']['name']}")
    st.write(f"**Next Recharge Date:** {user_data['recharge_date']}")
with col2:
    st.success("💰 **Balance & Data**")
    st.write(f"**Balance:** {user_data['balance']}")
    st.write(f"**Data Remaining:** {user_data['data_remaining']} GB")

st.subheader("📊 Usage & Billing Trends")
fig1 = px.line(x=[1, 2, 3, 4, 5], y=[4.5, 3.2, 2.8, 3.9, 2.3], markers=True, title="Data Usage (GB) - Last 5 Months")
fig1.update_layout(xaxis_title="Months", yaxis_title="GB Used")
st.plotly_chart(fig1, use_container_width=True)

fig2 = go.Figure()
fig2.add_trace(go.Bar(x=[1, 2, 3, 4, 5], y=[30, 25, 27, 28, 26], marker_color='orange'))
fig2.update_layout(title="Billing History ($) - Last 5 Months", xaxis_title="Months", yaxis_title="Amount ($)")
st.plotly_chart(fig2, use_container_width=True)

# Chatbot Button with Glow Effect
chatbot_css = """
<style>
    div[data-testid="stButton"] button {
        animation: glow 1s infinite alternate;
    }
    @keyframes glow {
        from { box-shadow: 0 0 10px #4CAF50; }
        to { box-shadow: 0 0 20px #4CAF50; }
    }
</style>
"""
st.markdown(chatbot_css, unsafe_allow_html=True)
if st.button("💬 Chat with AI Assistant"):
    st.session_state.chat_open = True
    st.rerun()

# Chat Window
if st.session_state.chat_open:
    st.sidebar.title("📢 AI Assistant Chat")
    chat_container = st.sidebar.container()
    for message in st.session_state.chat_history:
        role, text = message.split(':', 1)
        chat_container.markdown(f"**{role}:** {text}")
    
    user_input = st.sidebar.text_input("Type your message...", key="chat_input").strip()
    send_col, exit_col = st.sidebar.columns([3, 1])
    
    with send_col:
        if st.button("Send"):
            if user_input:
                st.session_state.chat_history.append(f"You: {user_input}")
                response = get_ai_response(user_input, phone)
                st.session_state.chat_history.append(f"AI Assistant: {response}")
                st.rerun()
    
    with exit_col:
        if st.button("Exit Chat"):
            st.session_state.chat_open = False
            st.rerun()

    # Notifications
    if not st.session_state.notifications:
        notification = random.choice([
            "We noticed you haven't recharged in a while. Here's a 10% discount on your next recharge!",
            "Special win-back offer: Get 2GB extra data if you recharge today!",
            "We miss you! Enjoy a bonus cashback on your next bill payment."
        ])
        st.session_state.notifications.append(notification)
    
    if st.session_state.notifications:
        st.sidebar.subheader("🔔 Notifications")
        for note in st.session_state.notifications:
            st.sidebar.warning(note)
