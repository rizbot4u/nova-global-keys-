"""NOVA Remittance API Routes"""
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Optional
import uuid

from remittance.core.engine import RemittanceEngine
from remittance.core.fbo import FBOAccountManager
from remittance.compliance.engine import ComplianceEngine
from ...thor_engine import get_current_user

router = APIRouter(prefix="/api/remit", tags=["Remittance"])
remit_engine = RemittanceEngine()
fbo_manager = FBOAccountManager()
compliance = ComplianceEngine()

@router.post("/wallet/create")
async def create_wallet(
    blockchain: str = "ETH",
    current_user: dict = Depends(get_current_user)
):
    """Create a wallet for sending/receiving funds"""
    result = await remit_engine.create_wallet(
        user_id=current_user['user_id'],
        blockchain=blockchain
    )
    return result

@router.post("/send")
async def send_funds(
    recipient_address: str,
    amount: float,
    source_chain: str = "ETH",
    dest_chain: str = "ETH",
    current_user: dict = Depends(get_current_user)
):
    """Send USDC to any address (cross-chain supported)"""
    
    # First, check FBO balance
    balance = await fbo_manager.get_customer_balance(current_user['user_id'])
    if balance['balance'] < amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")
    
    # Create transaction record
    tx_id = f"tx_{uuid.uuid4().hex[:16]}"
    
    # AML screening
    screen_result = await compliance.aml_screen({
        "tx_id": tx_id,
        "user_id": current_user['user_id'],
        "amount": amount,
        "recipient_address": recipient_address,
        "recipient_country": "UNKNOWN"  # In production, derive from address
    })
    
    if screen_result.get("needs_review"):
        # Flag for manual review, don't execute
        return {
            "success": False,
            "message": "Transaction flagged for compliance review",
            "tx_id": tx_id
        }
    
    # Execute transfer
    result = await remit_engine.send_cross_chain(
        sender_id=current_user['user_id'],
        recipient_address=recipient_address,
        amount=amount,
        source_chain=source_chain,
        dest_chain=dest_chain
    )
    
    if result.get("success"):
        # Debit customer balance
        await fbo_manager.debit_customer(
            user_id=current_user['user_id'],
            amount=amount,
            reference=f"send_{tx_id}"
        )
    
    return result

@router.post("/batch-payout")
async def batch_payout(
    recipients: List[Dict],
    current_user: dict = Depends(get_current_user)
):
    """Pay multiple recipients in one atomic transaction"""
    
    # Calculate total amount
    total = sum(r["amount"] for r in recipients)
    
    # Check balance
    balance = await fbo_manager.get_customer_balance(current_user['user_id'])
    if balance['balance'] < total:
        raise HTTPException(status_code=400, detail="Insufficient balance")
    
    # Execute batch
    result = await remit_engine.batch_payout(recipients)
    
    if result.get("success"):
        # Debit customer balance
        await fbo_manager.debit_customer(
            user_id=current_user['user_id'],
            amount=total,
            reference=f"batch_{result.get('batch_id')}"
        )
    
    return result

@router.get("/balance")
async def get_balance(current_user: dict = Depends(get_current_user)):
    """Get your current FBO balance"""
    balance = await fbo_manager.get_customer_balance(current_user['user_id'])
    return {"success": True, "balance": balance}

@router.get("/reconcile")
async def reconcile(current_user: dict = Depends(get_current_user)):
    """Reconcile customer balances (admin only)"""
    # In production, restrict to admin users
    result = await fbo_manager.reconcile()
    return result

@router.get("/transaction/{tx_id}")
async def get_transaction_status(tx_id: str):
    """Get real-time status of a transaction"""
    status = await remit_engine.get_transaction_status(tx_id)
    return status

@router.post("/kyc/submit")
async def submit_kyc(
    full_name: str,
    document_number: str,
    current_user: dict = Depends(get_current_user)
):
    """Submit KYC documents for verification"""
    result = await compliance.kyc_check({
        "user_id": current_user['user_id'],
        "full_name": full_name,
        "document_number": document_number
    })
    return result

@router.get("/kyc/status")
async def kyc_status(current_user: dict = Depends(get_current_user)):
    """Check KYC verification status"""
    kyc_key = f"kyc:user:{current_user['user_id']}"
    status = redis_client.hget(kyc_key, "status") or "not_submitted"
    return {"success": True, "status": status}
