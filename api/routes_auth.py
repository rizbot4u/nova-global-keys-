"""
Nova Global Keys - Authentication Routes
OAuth login and callback handling
"""

import uuid
import base64
import json
import logging
import httpx
from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse, JSONResponse, HTMLResponse
from config.settings import settings
from core.redis_client import redis_client

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.get("/login")
async def auth_login():
    """Redirect to Bybit OAuth"""
    state = uuid.uuid4().hex[:8]
    url = f"https://www.bybit.com/en/oauth?client_id={settings.CLIENT_ID}&response_type=code&scope=openapi&state={state}&redirect_uri={settings.REDIRECT_URI}&affiliate_id={settings.AFFILIATE_ID}"
    return RedirectResponse(url)

@router.get("/callback/bybit")
async def auth_callback(code: str, state: str):
    """Handle OAuth callback"""
    logger.info(f"OAuth callback: state={state}")
    
    # Check if this is from Telegram
    tg_user_id = redis_client.get_oauth_state(state)
    
    async with httpx.AsyncClient() as client:
        # Exchange code for token
        token_resp = await client.post(
            f"{settings.OAUTH_BASE}/oauth/v1/public/access_token",
            data={
                "grant_type": "authorization_code",
                "client_id": settings.CLIENT_ID,
                "client_secret": settings.CLIENT_SECRET,
                "code": code,
                "redirect_uri": settings.REDIRECT_URI
            }
        )
        
        if token_resp.status_code != 200:
            return JSONResponse(status_code=400, content={"error": "Token exchange failed"})
        
        token_data = token_resp.json()
        access_token = token_data.get('access_token')
        
        # Get API keys
        keys_resp = await client.get(
            f"{settings.OAUTH_BASE}/oauth/v1/resource/restrict/openapi",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        keys_data = keys_resp.json()
        result = keys_data.get("result", {})
        api_key = result.get("api_key")
        api_secret = result.get("api_secret")
        
        # Extract UID from token
        try:
            token_parts = access_token.split('.')
            payload = token_parts[1]
            payload += '=' * (4 - len(payload) % 4)
            decoded = base64.b64decode(payload)
            payload_data = json.loads(decoded)
            uid = str(payload_data.get('GrantMemberID', 'unknown'))
        except:
            uid = 'unknown'
        
        # Store for user
        if tg_user_id:
            redis_client.store_user_keys(tg_user_id, api_key, api_secret, uid)
            redis_client.delete_oauth_state(state)
            return JSONResponse(content={
                "success": True,
                "message": "Account connected to Telegram!",
                "uid": uid
            })
        else:
            # Web user - generate session and show success page
            session_id = uuid.uuid4().hex
            redis_client.store_user_keys(session_id, api_key, api_secret, uid)
            
            # Return beautiful HTML success page
            return HTMLResponse(content=f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Nova Global Keys - Authentication Successful</title>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <meta http-equiv="refresh" content="3;url=https://t.me/Novaglobalkeysbot">
                <style>
                    body {{
                        background: linear-gradient(135deg, #0b1120 0%, #1a2635 100%);
                        color: white;
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        min-height: 100vh;
                        margin: 0;
                        text-align: center;
                    }}
                    .container {{
                        max-width: 500px;
                        padding: 40px;
                    }}
                    .success-icon {{
                        font-size: 5em;
                        color: #4ade80;
                        margin-bottom: 20px;
                    }}
                    h1 {{
                        font-size: 2em;
                        margin-bottom: 20px;
                        background: linear-gradient(90deg, #60a5fa, #22d3ee);
                        -webkit-background-clip: text;
                        -webkit-text-fill-color: transparent;
                    }}
                    p {{
                        color: #94a3b8;
                        margin: 20px 0;
                        line-height: 1.6;
                    }}
                    .btn {{
                        display: inline-block;
                        background: #26A5E4;
                        color: white;
                        padding: 12px 30px;
                        border-radius: 8px;
                        text-decoration: none;
                        font-weight: bold;
                        margin-top: 20px;
                    }}
                    .broker-badge {{
                        display: inline-block;
                        background: #F7A600;
                        color: black;
                        padding: 5px 15px;
                        border-radius: 20px;
                        font-size: 0.9em;
                        margin-bottom: 20px;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="broker-badge">Official Bybit Broker • Kr000820</div>
                    <div class="success-icon">✅</div>
                    <h1>Authentication Successful!</h1>
                    <p>Your Bybit account is now connected to Nova Global Keys.</p>
                    <p>Return to Telegram to start trading with your connected account.</p>
                    <a href="https://t.me/Novaglobalkeysbot" class="btn">Open @Novaglobalkeysbot</a>
                    <p style="margin-top: 30px; font-size: 0.8em; color: #64748b;">
                        🙏 Love, Peace & Respect<br>
                        You will be redirected automatically in 3 seconds...
                    </p>
                </div>
            </body>
            </html>
            """)
