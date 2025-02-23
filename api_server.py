from fastapi import FastAPI
from pydantic import BaseModel
import random

app = FastAPI()

# Dummy Data
customer_data = {
    "9876543210": {"plan": "Unlimited Talk & 5GB Data", "discounts": 0, "support_tickets": []},
    "8765432109": {"plan": "Unlimited Talk & 10GB Data", "discounts": 0, "support_tickets": []}
}

class PlanUpdateRequest(BaseModel):
    phone: str
    new_plan: str

class RetentionRequest(BaseModel):
    phone: str

class NetworkResetRequest(BaseModel):
    phone: str

@app.get("/")
def root():
    return {"message": "Welcome to the Telecom API Server"}

@app.post("/plan/update")
def update_plan(request: PlanUpdateRequest):
    if request.phone in customer_data:
        customer_data[request.phone]["plan"] = request.new_plan
        return {"status": "success", "message": f"Plan updated to {request.new_plan}"}
    return {"status": "error", "message": "Phone number not found"}

@app.post("/retention/apply_discount")
def apply_discount(request: RetentionRequest):
    if request.phone in customer_data:
        discount = random.choice([10, 20, 30])  # Random discount percentage
        customer_data[request.phone]["discounts"] += discount
        return {"status": "success", "message": f"{discount}% discount applied"}
    return {"status": "error", "message": "Phone number not found"}

@app.post("/network/reset")
def reset_network(request: NetworkResetRequest):
    if request.phone in customer_data:
        ticket_id = f"NET-{random.randint(1000, 9999)}"
        customer_data[request.phone]["support_tickets"].append(ticket_id)
        return {"status": "success", "message": f"Network reset request received. Ticket ID: {ticket_id}"}
    return {"status": "error", "message": "Phone number not found"}

