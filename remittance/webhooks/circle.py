"""Webhook handler for Circle events"""
from fastapi import APIRouter, Request, HTTPException
import hmac
import hashlib
import os
import json

router = APIRouter(prefix="/webhooks/circle", tags=["Webhooks"])

CIRCLE_WEBHOOK_SECRET = os.getenv("CIRCLE_WEBHOOK_SECRET", "")

def verify_signature(payload: bytes, signature: str) -> bool:
    """Verify Circle webhook signature"""
    expected = hmac.new(
        CIRCLE_WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(signature, expected)

@router.post("/transfer")
async def handle_transfer(request: Request):
    """Handle transfer completion notifications"""
    payload = await request.body()
    signature = request.headers.get("X-Circle-Signature", "")
    
    if not verify_signature(payload, signature):
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    data = json.loads(payload)
    
    # Update transaction status in database
    tx_id = data.get("id")
    status = data.get("status")
    
    # Log for debugging
    print(f"✅ Transfer {tx_id} status: {status}")
    
    return {"received": True}

@router.post("/wallet")
async def handle_wallet(request: Request):
    """Handle wallet creation/update notifications"""
    payload = await request.body()
    signature = request.headers.get("X-Circle-Signature", "")
    
    if not verify_signature(payload, signature):
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    data = json.loads(payload)
    print(f"💰 Wallet webhook: {data.get('type')}")
    
    return {"received": True}
