import requests
from customer_data import retrieve_user_context

API_BASE_URL = "http://localhost:8000"


def get_ai_response(prompt, phone):
    """Fetch AI-generated response based on user context and API interactions"""
    try:
        context = retrieve_user_context(phone)
        system_prompt = f"""
        You are an AI assistant for a mobile service provider.
        Be helpful, professional, and concise in your responses.
        Offer proactive solutions based on user history and plan details.
        Use the following user context to provide personalized responses:
        {context}
        """
        
        formatted_prompt = f"{system_prompt}\n\nCustomer: {prompt}\nAssistant:"

        # Fetch AI response
        ai_response = requests.post(
            "http://localhost:11434/api/chat",
            json={
                "model": "llama3",
                "messages": [
                    {"role": "user", "content": formatted_prompt}
                ],
                "stream": False
            }
        )

        # Handle AI response
        if ai_response.status_code == 200:
            result = ai_response.json()
            response_text = result.get('message', {}).get('content', '')
        else:
            response_text = "I'm unable to fetch a response at the moment."

        # Fetch retention offer from API
        retention_response = requests.post(f"{API_BASE_URL}/retention/apply_discount", json={"phone": phone})
        if retention_response.status_code == 200:
            retention_offer = retention_response.json().get("message", "")
            response_text += f"\n\n{retention_offer}"

        # Fetch network reset status from API
        network_response = requests.post(f"{API_BASE_URL}/network/reset", json={"phone": phone})
        if network_response.status_code == 200:
            network_status = network_response.json().get("message", "")
            response_text += f"\n\n{network_status}"

        return response_text
    
    except Exception as e:
        return "An error occurred while processing your request."