import redis
import os
import logging
import httpx

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("broker-check")

# Load Redis credentials from .env
REDIS_URL = os.getenv("REDIS_URL", "redis://default:NovaGlobal2026@localhost:6379/0")
r = redis.from_url(REDIS_URL, decode_responses=True)

# Broker code and API keys
BROKER_CODE = os.getenv("BROKER_CODE", "Kr000820")
API_KEY = os.getenv("MASTER_API_KEY")
API_SECRET = os.getenv("MASTER_API_SECRET")

def check_and_repair_broker():
    key = f"broker:{BROKER_CODE}"
    mapping = r.get(key)

    if mapping:
        logger.info(f"✅ Broker {BROKER_CODE} mapping found in Redis: {mapping}")
    else:
        logger.warning(f"⚠️ Broker {BROKER_CODE} has NO mapping in Redis!")
        if API_KEY and API_SECRET:
            # Auto-repair: insert mapping into Redis
            value = f"{API_KEY}:{API_SECRET}"
            r.set(key, value)
            logger.info(f"🔧 Inserted broker mapping into Redis: {key} -> {value}")
        else:
            logger.error("❌ No API key/secret found in .env. Cannot repair mapping.")

def verify_bybit_credentials():
    if not API_KEY or not API_SECRET:
        logger.error("❌ Missing API key/secret, cannot verify with Bybit.")
        return

    url = "https://api.bybit.com/v5/account/info"
    headers = {
        "X-BAPI-API-KEY": API_KEY,
        "X-BAPI-API-SECRET": API_SECRET,
    }

    try:
        resp = httpx.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            logger.info("✅ Bybit credentials verified successfully.")
            logger.info(f"Response: {resp.json()}")
        else:
            logger.error(f"❌ Bybit verification failed: {resp.status_code} {resp.text}")
    except Exception as e:
        logger.error(f"❌ Error verifying Bybit credentials: {e}")

if __name__ == "__main__":
    check_and_repair_broker()
    verify_bybit_credentials()
