#!/usr/bin/env python3
"""
NOVA GLOBAL KEYS - Broker Service
Manages subaccounts, fee settings, agent commissions
"""

import os
import sys
import logging
import uuid
from datetime import datetime
from typing import Optional, List
from fastapi import FastAPI, HTTPException, Depends, Header
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Add shared modules to path
sys.path.append("/root/nova-global-keys-/services")
from shared.utils.bybit import ThorEngine
from shared.redis.client import redis_client

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("broker-service")

# FastAPI app
app = FastAPI(title="Nova Broker Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()

# Pydantic models
class SubAccountCreate(BaseModel):
    username: str
    member_type: int = 1
    note: str = ""

class FeeRateConfig(BaseModel):
    sub_uid: str
    fee_rate: dict

class TransferRequest(BaseModel):
    from_account_type: str
    to_account_type: str
    coin: str
    amount: str
    transfer_id: Optional[str] = None

# Configuration
MASTER_API_KEY = os.getenv("MASTER_API_KEY", "")
MASTER_API_SECRET = os.getenv("MASTER_API_SECRET", "")
BROKER_CODE = os.getenv("BROKER_CODE", "Kr000820")
AFFILIATE_ID = os.getenv("AFFILIATE_ID", "127146")

# Auth for broker endpoints (admin only)
async def verify_master_key(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    token = authorization.replace("Bearer ", "")
    
    # Simple API key check for master endpoints
    if token != MASTER_API_KEY:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    return {"role": "master"}

# ============================================================================
# ENDPOINTS
# ============================================================================

@app.get("/health")
async def health():
    return {
        "service": "broker",
        "status": "healthy",
        "redis": redis_client.ping(),
        "timestamp": datetime.now().isoformat()
    }

@app.post("/subaccount/create")
async def create_subaccount(
    request: SubAccountCreate,
    _: dict = Depends(verify_master_key)
):
    engine = ThorEngine(MASTER_API_KEY, MASTER_API_SECRET)
    try:
        result = await engine.create_subaccount(
            username=request.username,
            member_type=request.member_type,
            note=request.note
        )
        
        if result.get('retCode') == 0:
            sub_data = result.get('result', {})
            # Store in Redis for quick lookup
            sub_uid = sub_data.get('subMemberId')
            if sub_uid:
                redis_client.client.hset("broker:subaccounts", sub_uid, request.username)
            
            return result
        
        raise HTTPException(status_code=400, detail=result.get('retMsg', 'Creation failed'))
    finally:
        await engine.close()

@app.get("/subaccount/list")
async def list_subaccounts(_: dict = Depends(verify_master_key)):
    engine = ThorEngine(MASTER_API_KEY, MASTER_API_SECRET)
    try:
        result = await engine.get_subaccount_list()
        return result
    finally:
        await engine.close()

@app.post("/subaccount/fee")
async def set_subaccount_fee(
    request: FeeRateConfig,
    _: dict = Depends(verify_master_key)
):
    engine = ThorEngine(MASTER_API_KEY, MASTER_API_SECRET)
    try:
        result = await engine.set_subaccount_fee(
            sub_uid=request.sub_uid,
            fee_rate=request.fee_rate
        )
        return result
    finally:
        await engine.close()

@app.post("/transfer/universal")
async def universal_transfer(
    request: TransferRequest,
    _: dict = Depends(verify_master_key)
):
    engine = ThorEngine(MASTER_API_KEY, MASTER_API_SECRET)
    try:
        transfer_id = request.transfer_id or f"transfer_{uuid.uuid4().hex[:8]}"
        data = {
            "transferId": transfer_id,
            "fromAccountType": request.from_account_type,
            "toAccountType": request.to_account_type,
            "coin": request.coin,
            "amount": request.amount
        }
        result = await engine._request("POST", "/v5/asset/transfer/universal-transfer", data=data)
        return result
    finally:
        await engine.close()

@app.post("/transfer/to-subaccount")
async def transfer_to_subaccount(
    coin: str,
    amount: str,
    sub_account_id: str,
    transfer_id: Optional[str] = None,
    _: dict = Depends(verify_master_key)
):
    engine = ThorEngine(MASTER_API_KEY, MASTER_API_SECRET)
    try:
        transfer_id = transfer_id or f"sub_{uuid.uuid4().hex[:8]}"
        data = {
            "transferId": transfer_id,
            "coin": coin,
            "amount": amount,
            "subMemberId": sub_account_id
        }
        result = await engine._request("POST", "/v5/asset/transfer/inter-proxy-transfer", data=data)
        return result
    finally:
        await engine.close()

@app.get("/affiliate/commission")
async def get_affiliate_commission(
    limit: int = 50,
    _: dict = Depends(verify_master_key)
):
    engine = ThorEngine(MASTER_API_KEY, MASTER_API_SECRET)
    try:
        result = await engine.get_affiliate_commission(limit=limit)
        return result
    finally:
        await engine.close()

@app.get("/affiliate/users")
async def get_affiliate_users(
    size: int = 50,
    page: int = 1,
    _: dict = Depends(verify_master_key)
):
    engine = ThorEngine(MASTER_API_KEY, MASTER_API_SECRET)
    try:
        result = await engine.get_affiliate_user_list(size=size, page=page)
        return result
    finally:
        await engine.close()

if __name__ == "__main__":
    port = int(os.getenv("BROKER_SERVICE_PORT", 8006))
    uvicorn.run("main:app", host="127.0.0.1", port=port, reload=True)
