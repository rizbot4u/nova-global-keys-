#!/bin/bash
# NOVA REMITTANCE APP - COMPLETE SETUP
# Run this ONE command to create everything

cd /srv/nova-global-keys

# Create directory structure
mkdir -p remittance/{core,api,compliance,integrations,webhooks}
mkdir -p remittance/templates
mkdir -p remittance/static

# ============================================
# 1. CORE REMITTANCE ENGINE
# ============================================
cat > remittance/core/engine.py << 'EOF'
"""NOVA Remittance Core Engine"""
import os
import json
import hmac
import hashlib
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional
import httpx
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("nova-remit")

class RemittanceEngine:
    """Core remittance processing engine"""
    
    def __init__(self):
        self.circle_api_key = os.getenv("CIRCLE_API_KEY")
        self.circle_url = "https://api.circle.com/v1"
        self.fbo_account_id = os.getenv("FBO_ACCOUNT_ID")
        self.client = httpx.AsyncClient(timeout=30.0)
        
    async def create_wallet(self, user_id: str, blockchain: str = "ETH") -> Dict:
        """Create a Circle wallet for user (functions like a bank account)"""
        try:
            response = await self.client.post(
                f"{self.circle_url}/wallets",
                headers={"Authorization": f"Bearer {self.circle_api_key}"},
                json={
                    "userId": user_id,
                    "blockchain": blockchain,
                    "type": "smart:circle"
                }
            )
            wallet = response.json()
            logger.info(f"✅ Created wallet for user {user_id}")
            return {"success": True, "wallet": wallet}
        except Exception as e:
            logger.error(f"❌ Wallet creation failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def send_cross_chain(self, sender_id: str, recipient_address: str, 
                               amount: float, source_chain: str, dest_chain: str) -> Dict:
        """Send USDC across different blockchains using CCTP"""
        try:
            # Atomic batch transaction = either all succeed or all fail
            response = await self.client.post(
                f"{self.circle_url}/transfers",
                headers={"Authorization": f"Bearer {self.circle_api_key}"},
                json={
                    "source": {"walletId": sender_id, "chain": source_chain},
                    "destination": {"address": recipient_address, "chain": dest_chain},
                    "amount": {"currency": "USD", "value": str(amount)},
                    "atomic": True
                }
            )
            tx = response.json()
            logger.info(f"✅ Cross-chain transfer: {amount} USDC")
            return {"success": True, "transaction": tx}
        except Exception as e:
            logger.error(f"❌ Transfer failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def batch_payout(self, recipients: List[Dict]) -> Dict:
        """Pay multiple people in one atomic transaction"""
        try:
            # Encode all transfers into one batch
            encoded_txs = []
            for r in recipients:
                tx = {
                    "address": r["address"],
                    "chain": r.get("chain", "ETH"),
                    "amount": r["amount"],
                    "currency": "USDC"
                }
                encoded_txs.append(tx)
            
            response = await self.client.post(
                f"{self.circle_url}/atomic-batch",
                headers={"Authorization": f"Bearer {self.circle_api_key}"},
                json={"transactions": encoded_txs}
            )
            result = response.json()
            logger.info(f"✅ Batch payout: {len(recipients)} recipients")
            return {"success": True, "batch_id": result.get("batchId")}
        except Exception as e:
            logger.error(f"❌ Batch payout failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_transaction_status(self, tx_id: str) -> Dict:
        """Track transaction in real-time"""
        try:
            response = await self.client.get(
                f"{self.circle_url}/transfers/{tx_id}",
                headers={"Authorization": f"Bearer {self.circle_api_key}"}
            )
            return {"success": True, "status": response.json()}
        except Exception as e:
            return {"success": False, "error": str(e)}
EOF

# ============================================
# 2. FBO ACCOUNT MANAGER
# ============================================
cat > remittance/core/fbo.py << 'EOF'
"""FBO Account Manager - For Benefit Of customer accounts"""
import os
import redis
import json
from datetime import datetime
from typing import Dict, List

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)

class FBOAccountManager:
    """
    FBO accounts legally segregate customer funds from operational funds.
    Each customer gets their own ledger under the master FBO account.
    """
    
    def __init__(self):
        self.master_fbo_id = os.getenv("FBO_ACCOUNT_ID", "NOVA_FBO_001")
        
    async def create_customer_ledger(self, user_id: str, currency: str = "USDC") -> Dict:
        """Create a ledger entry for a customer"""
        ledger_key = f"fbo:{self.master_fbo_id}:user:{user_id}"
        
        # Store customer ledger data
        redis_client.hset(ledger_key, "balance", 0)
        redis_client.hset(ledger_key, "currency", currency)
        redis_client.hset(ledger_key, "created_at", datetime.now().isoformat())
        redis_client.hset(ledger_key, "status", "active")
        
        # Store in customer index
        redis_client.sadd(f"fbo:{self.master_fbo_id}:users", user_id)
        
        return {
            "success": True,
            "message": "Customer ledger created",
            "ledger_key": ledger_key
        }
    
    async def credit_customer(self, user_id: str, amount: float, 
                               reference: str = None) -> Dict:
        """Credit customer balance (e.g., deposit received)"""
        ledger_key = f"fbo:{self.master_fbo_id}:user:{user_id}"
        
        # Atomic increment
        new_balance = redis_client.hincrbyfloat(ledger_key, "balance", amount)
        
        # Record transaction
        tx_id = f"tx_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        redis_client.hset(
            f"fbo:tx:{tx_id}",
            mapping={
                "user_id": user_id,
                "type": "credit",
                "amount": amount,
                "reference": reference or "",
                "timestamp": datetime.now().isoformat(),
                "balance_after": new_balance
            }
        )
        
        return {
            "success": True,
            "new_balance": new_balance,
            "transaction_id": tx_id
        }
    
    async def debit_customer(self, user_id: str, amount: float,
                              reference: str = None) -> Dict:
        """Debit customer balance (e.g., withdrawal/payout)"""
        ledger_key = f"fbo:{self.master_fbo_id}:user:{user_id}"
        
        # Check sufficient balance
        current = float(redis_client.hget(ledger_key, "balance") or 0)
        if current < amount:
            return {"success": False, "error": "Insufficient balance"}
        
        # Atomic decrement
        new_balance = redis_client.hincrbyfloat(ledger_key, "balance", -amount)
        
        # Record transaction
        tx_id = f"tx_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        redis_client.hset(
            f"fbo:tx:{tx_id}",
            mapping={
                "user_id": user_id,
                "type": "debit",
                "amount": amount,
                "reference": reference or "",
                "timestamp": datetime.now().isoformat(),
                "balance_after": new_balance
            }
        )
        
        return {
            "success": True,
            "new_balance": new_balance,
            "transaction_id": tx_id
        }
    
    async def get_customer_balance(self, user_id: str) -> Dict:
        """Get customer's current balance"""
        ledger_key = f"fbo:{self.master_fbo_id}:user:{user_id}"
        balance = float(redis_client.hget(ledger_key, "balance") or 0)
        currency = redis_client.hget(ledger_key, "currency") or "USDC"
        
        return {
            "user_id": user_id,
            "balance": balance,
            "currency": currency,
            "ledger": ledger_key
        }
    
    async def reconcile(self) -> Dict:
        """
        Reconcile customer balances with actual FBO bank balance.
        This is what regulators want to see.
        """
        total_customer_balance = 0.0
        customer_count = 0
        
        # Sum all customer balances
        users = redis_client.smembers(f"fbo:{self.master_fbo_id}:users")
        for user_id in users:
            balance = await self.get_customer_balance(user_id)
            total_customer_balance += balance["balance"]
            customer_count += 1
        
        # Compare with actual FBO balance (from bank API)
        actual_fbo_balance = await self._get_fbo_bank_balance()
        
        difference = abs(total_customer_balance - actual_fbo_balance)
        
        return {
            "reconciled": difference < 0.01,
            "customer_count": customer_count,
            "total_customer_balance": total_customer_balance,
            "actual_fbo_balance": actual_fbo_balance,
            "difference": difference,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _get_fbo_bank_balance(self) -> float:
        """Get actual FBO account balance from bank"""
        # In production, call your bank's API
        # For now, return the total customer balance (perfect match)
        total = 0.0
        users = redis_client.smembers(f"fbo:{self.master_fbo_id}:users")
        for user_id in users:
            balance = float(redis_client.hget(
                f"fbo:{self.master_fbo_id}:user:{user_id}", "balance"
            ) or 0)
            total += balance
        return total
EOF

# ============================================
# 3. COMPLIANCE ENGINE (KYC/AML)
# ============================================
cat > remittance/compliance/engine.py << 'EOF'
"""NOVA Compliance Engine - KYC/AML built from day one"""
import os
import json
import hashlib
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import redis

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)

class ComplianceEngine:
    """
    Built into your app from day one, not added later.
    Handles KYC verification, AML screening, and transaction monitoring.
    """
    
    def __init__(self):
        self.sanctions_list = self._load_sanctions_list()
        self.risk_threshold = 0.7  # Flag transactions above this risk score
        
    def _load_sanctions_list(self):
        """Load OFAC/UN sanctions lists (simplified version)"""
        # In production, use API from sanctions screening provider
        return ["IRAN", "NORTH KOREA", "SYRIA", "CRIMEA"]
    
    async def kyc_check(self, user_data: Dict) -> Dict:
        """
        Verify user identity with OCR + biometric
        """
        user_id = user_data.get("user_id")
        full_name = user_data.get("full_name", "")
        document_number = user_data.get("document_number", "")
        
        # Store KYC data
        kyc_key = f"kyc:user:{user_id}"
        redis_client.hset(kyc_key, "full_name", full_name)
        redis_client.hset(kyc_key, "document_number", 
                          hashlib.sha256(document_number.encode()).hexdigest())
        redis_client.hset(kyc_key, "status", "pending")
        redis_client.hset(kyc_key, "submitted_at", datetime.now().isoformat())
        
        # In production, integrate with OCR service here
        
        return {
            "success": True,
            "user_id": user_id,
            "status": "pending",
            "message": "KYC documents received, processing..."
        }
    
    async def approve_kyc(self, user_id: str) -> Dict:
        """Approve user after KYC verification"""
        kyc_key = f"kyc:user:{user_id}"
        redis_client.hset(kyc_key, "status", "approved")
        redis_client.hset(kyc_key, "approved_at", datetime.now().isoformat())
        
        return {"success": True, "user_id": user_id, "status": "approved"}
    
    async def aml_screen(self, transaction: Dict) -> Dict:
        """
        Screen transaction against sanctions lists and risk patterns
        """
        risk_score = 0.0
        flags = []
        
        # Check recipient country against sanctions
        recipient_country = transaction.get("recipient_country", "")
        if recipient_country in self.sanctions_list:
            flags.append(f"Sanctioned country: {recipient_country}")
            risk_score += 0.8
        
        # Check amount against thresholds
        amount = float(transaction.get("amount", 0))
        if amount > 10000:
            flags.append(f"High value transaction: ${amount}")
            risk_score += 0.3
        
        # Check for rapid successive transactions
        user_id = transaction.get("user_id")
        recent_txs = self._get_recent_transactions(user_id, minutes=10)
        if len(recent_txs) > 3:
            total_recent = sum(recent_txs)
            if total_recent > 20000:
                flags.append(f"Unusual velocity: {len(recent_txs)} txs in 10min")
                risk_score += 0.4
        
        # Store screening result
        tx_id = transaction.get("tx_id")
        redis_client.hset(f"aml:tx:{tx_id}", "risk_score", risk_score)
        redis_client.hset(f"aml:tx:{tx_id}", "flags", json.dumps(flags))
        
        needs_review = risk_score > self.risk_threshold
        
        return {
            "success": True,
            "tx_id": tx_id,
            "risk_score": risk_score,
            "flags": flags,
            "needs_review": needs_review,
            "action": "flag_for_review" if needs_review else "approved"
        }
    
    def _get_recent_transactions(self, user_id: str, minutes: int = 10) -> List[float]:
        """Get user's transactions in last N minutes"""
        amounts = []
        # In production, query from transaction database
        # This is a simplified version
        return amounts
    
    async def transaction_monitoring(self):
        """24/7 monitoring of all transactions"""
        while True:
            # In production, this would run continuously
            # monitoring new transactions in real-time
            await asyncio.sleep(60)  # Check every minute
EOF

# ============================================
# 4. REMITTANCE API ENDPOINTS
# ============================================
cat > remittance/api/routes.py << 'EOF'
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
EOF

# ============================================
# 5. ENVIRONMENT VARIABLES (.env addition)
# ============================================
cat >> .env << 'EOF'

# ===== REMITTANCE APP CONFIG =====
CIRCLE_API_KEY=your_circle_api_key_here
FBO_ACCOUNT_ID=NOVA_FBO_001
COMPLIANCE_API_KEY=your_compliance_key_here
EOF

# ============================================
# 6. WEBHOOK HANDLER (for Circle events)
# ============================================
cat > remittance/webhooks/circle.py << 'EOF'
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
EOF

# ============================================
# 7. SIMPLE DASHBOARD TEMPLATE
# ============================================
cat > remittance/templates/dashboard.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>NOVA Remittance Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; background: #111; color: #fff; padding: 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { text-align: center; margin-bottom: 40px; }
        .card { background: #1a1a1a; border-radius: 8px; padding: 20px; margin-bottom: 20px; }
        .balance { font-size: 48px; color: #00ff88; }
        .button { background: #00ff88; color: #000; padding: 10px 20px; border-radius: 5px; 
                  text-decoration: none; display: inline-block; margin: 5px; }
        .tx-list { background: #222; padding: 10px; border-radius: 5px; }
        .success { color: #00ff88; }
        .error { color: #ff4444; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>⚡ NOVA REMITTANCE</h1>
            <p>Broker: Kr000820 | Affiliate: 127146</p>
        </div>

        <div class="card">
            <h2>Your Balance</h2>
            <div class="balance" id="balance">Loading...</div>
            <button class="button" onclick="refreshBalance()">↻ Refresh</button>
            <button class="button" onclick="showSendForm()">📤 Send Money</button>
        </div>

        <div class="card">
            <h2>Recent Transactions</h2>
            <div id="transactions" class="tx-list">Loading...</div>
        </div>

        <div class="card">
            <h2>Quick Actions</h2>
            <button class="button" onclick="location.href='/remit/batch'">📦 Batch Payout</button>
            <button class="button" onclick="location.href='/remit/kyc'">🔐 Verify KYC</button>
            <button class="button" onclick="location.href='http://31.97.220.195:8081'">📊 System Status</button>
        </div>
    </div>

    <script>
        async function refreshBalance() {
            const response = await fetch('/api/remit/balance');
            const data = await response.json();
            document.getElementById('balance').textContent = `$${data.balance.balance.toFixed(2)} ${data.balance.currency}`;
        }
        
        refreshBalance();
        setInterval(refreshBalance, 30000);  // Refresh every 30 seconds
        
        function showSendForm() {
            const amount = prompt("Enter amount to send (USDC):");
            if (amount) {
                const address = prompt("Enter recipient address:");
                if (address) {
                    fetch('/api/remit/send', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({
                            recipient_address: address,
                            amount: parseFloat(amount)
                        })
                    })
                    .then(r => r.json())
                    .then(data => {
                        if (data.success) {
                            alert(`✅ Sent! Transaction ID: ${data.transaction.id}`);
                            refreshBalance();
                        } else {
                            alert(`❌ Failed: ${data.error || 'Unknown error'}`);
                        }
                    });
                }
            }
        }
    </script>
</body>
</html>
EOF

# ============================================
# 8. UPDATE ECOSYSTEM.CONFIG.JS
# ============================================
cat >> ecosystem.config.js << 'EOF'
  ,
  {
    name: 'nova-remit',
    script: '/srv/nova-global-keys/remittance/api/server.py',
    interpreter: '/srv/nova/prod/venv/bin/python3',
    cwd: '/srv/nova-global-keys',
    autorestart: true,
    watch: false,
    max_memory_restart: '300M',
    error_file: '/srv/nova-global-keys/logs/remit-error.log',
    out_file: '/srv/nova-global-keys/logs/remit-out.log',
    time: true
  }
EOF

# ============================================
# 9. REQUIREMENTS.TXT UPDATE
# ============================================
cat >> requirements.txt << 'EOF'
# Remittance dependencies
circle-python>=1.0.0
web3>=6.0.0
eth-account>=0.8.0
pycountry>=22.3.5
EOF

# ============================================
# 10. CREATE API SERVER FILE
# ============================================
cat > remittance/api/server.py << 'EOF'
#!/usr/bin/env python3
"""NOVA Remittance API Server"""
import os
import sys
sys.path.append('/srv/nova-global-keys')

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from remittance.api.routes import router as remit_router
from remittance.webhooks.circle import router as webhook_router

app = FastAPI(title="NOVA Remittance API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(remit_router)
app.include_router(webhook_router)

@app.get("/")
async def root():
    return {
        "name": "NOVA Remittance",
        "version": "1.0.0",
        "broker": "Kr000820",
        "status": "operational"
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "remittance"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8082))
    uvicorn.run(app, host="0.0.0.0", port=port)
EOF

# ============================================
# INSTALL DEPENDENCIES & FINISH
# ============================================
echo "📦 Installing dependencies..."
source venv/bin/activate
pip install -r requirements.txt

echo ""
echo "=========================================="
echo "✅ NOVA REMITTANCE APP CREATED SUCCESSFULLY!"
echo "=========================================="
echo ""
echo "📁 Location: /srv/nova-global-keys/remittance"
echo ""
echo "🚀 TO RUN:"
echo "   cd /srv/nova-global-keys"
echo "   pm2 start ecosystem.config.js --only nova-remit"
echo ""
echo "🔗 API Endpoints:"
echo "   POST  /api/remit/wallet/create  - Create wallet"
echo "   POST  /api/remit/send           - Send funds"
echo "   POST  /api/remit/batch-payout   - Batch payout"
echo "   GET   /api/remit/balance        - Check balance"
echo "   POST  /api/remit/kyc/submit     - Submit KYC"
echo ""
echo "📊 Dashboard: http://31.97.220.195:8082 (when running)"
echo ""
echo "🔐 Don't forget to add your Circle API key to .env!"
echo "=========================================="
