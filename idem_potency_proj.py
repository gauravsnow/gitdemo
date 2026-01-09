from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
import redis
import json
import hashlib
import uuid
from datetime import datetime

# Create FastAPI app
app = FastAPI()

# Connect to Redis
r = redis.Redis(host="localhost", port=6379, decode_responses=True)

TTL_SECONDS = 3600  # 1 hour


# Request body model
class PaymentRequest(BaseModel):
    orderId: str
    amount: int


# Create hash of request body
def request_hash(data: dict):
    return hashlib.sha256(
        json.dumps(data, sort_keys=True).encode()
    ).hexdigest()


# Fake payment creation
def create_payment(req: PaymentRequest):
    return {
        "paymentId": f"PAY-{uuid.uuid4()}",
        "status": "SUCCESS",
        "orderId": req.orderId,
        "amount": req.amount,
        "createdAt": datetime.utcnow().isoformat()
    }


# Payment API
@app.post("/pay")
def pay(
    req: PaymentRequest,
    idempotency_key: str = Header(None, alias="Idempotency-Key")
):
    if not idempotency_key:
        raise HTTPException(400, "Missing Idempotency-Key")

    redis_key = f"idem:{idempotency_key}"
    lock_key = f"lock:{idempotency_key}"
    body_hash = request_hash(req.dict())

    # 1️⃣ Check replay
    cached = r.get(redis_key)
    if cached:
        data = json.loads(cached)
        if data["hash"] != body_hash:
            raise HTTPException(409, "Same key used with different request")
        return {"replay": True, **data["response"]}

    # 2️⃣ Acquire lock
    if not r.set(lock_key, "1", nx=True, ex=10):
        raise HTTPException(409, "Request already in progress")

    try:
        # 3️⃣ Create payment
        response = create_payment(req)

        # 4️⃣ Store in Redis
        r.set(
            redis_key,
            json.dumps({
                "hash": body_hash,
                "response": response
            }),
            ex=TTL_SECONDS
        )

        return {"replay": False, **response}

    finally:
        # 5️⃣ Release lock
        r.delete(lock_key)

