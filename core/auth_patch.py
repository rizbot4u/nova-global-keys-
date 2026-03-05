@app.get("/api/auth/callback/bybit")
async def auth_callback(code: str, state: str):
    logger.info(f"OAuth callback: state={state}, code={code[:5]}...")
    
    raw_tg_user_id = redis_client.get_oauth_state(state)
    tg_user_id = raw_tg_user_id.decode() if isinstance(raw_tg_user_id, bytes) else raw_tg_user_id
    
    timeout = httpx.Timeout(60.0, connect=30.0)
    async with httpx.AsyncClient(timeout=timeout, trust_env=True) as client:
        try:
            # 1. Exchange Token
            token_resp = await client.post(
                f"{settings.BYBIT_OAUTH}/oauth/v1/public/access_token",
                data={
                    "grant_type": "authorization_code",
                    "client_id": settings.CLIENT_ID,
                    "client_secret": settings.CLIENT_SECRET,
                    "code": code,
                    "redirect_uri": settings.REDIRECT_URI
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            token_data = token_resp.json()
            access_token = token_data.get('access_token')

            if not access_token:
                logger.error(f"Token exchange failed: {token_data}")
                return JSONResponse(status_code=400, content={"error": "Token exchange failed"})

            # 2. Get API keys
            keys_resp = await client.get(
                f"{settings.BYBIT_OAUTH}/oauth/v1/resource/restrict/openapi",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            keys_data = keys_resp.json()
            api_key = keys_data.get("result", {}).get("api_key")
            api_secret = keys_data.get("result", {}).get("api_secret")

            # 3. Get UID
            uid_resp = await client.get(
                f"{settings.BYBIT_OAUTH}/oauth/v1/resource/restrict/uid_bearer",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            uid = uid_resp.json().get("uid", "")

            # 4. Storage & Redirect
            if tg_user_id:
                redis_client.store_user_keys(tg_user_id, api_key, api_secret, uid)
                redis_client.delete_oauth_state(state)
                return HTMLResponse("<html><body><h1>Success!</h1><p>Telegram Connected.</p></body></html>")
            else:
                session_id = f"web_{uuid.uuid4().hex[:12]}"
                redis_client.store_user_keys(session_id, api_key, api_secret, uid)
                return RedirectResponse(url=f"https://novatradingkeys.com/dashboard?session={session_id}")

        except httpx.ConnectTimeout:
            logger.error("Bybit Connection Timeout")
            return JSONResponse(status_code=504, content={"error": "Bybit Timeout"})
        except Exception as e:
            logger.error(f"Auth Error: {str(e)}")
            return JSONResponse(status_code=500, content={"error": "Internal Server Error"})
