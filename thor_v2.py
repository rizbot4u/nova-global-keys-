from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from contextlib import asynccontextmanager
import datetime
import time
import asyncio
import uvicorn
import os
import psutil
import redis
import json

# Redis connection
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)

# Simple list to keep the last 20 logs
logs_cache = []
MAX_LOGS = 20

def add_log(message):
    """Add a log message with timestamp to the cache"""
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    formatted_log = f"[{timestamp}] {message}"
    logs_cache.append(formatted_log)
    if len(logs_cache) > MAX_LOGS:
        logs_cache.pop(0)

class ThorState:
    def __init__(self):
        self.start_time = None
        self.status = "initializing"
        self.request_count = 0
        self.error_count = 0
        self.last_errors = []

state = ThorState()

@asynccontextmanager
async def lifespan(app: FastAPI):
    state.start_time = datetime.datetime.now()
    state.status = "operational"
    add_log("🚀 Thor Engine Singleton Started - Dashboard Live")
    print(f"⚡ Thor Engine Singleton Started at {state.start_time}")
    yield
    add_log("🛑 Thor Engine Singleton Shutting Down")
    print("🛑 Thor Engine Singleton Shutting Down")

app = FastAPI(lifespan=lifespan)

@app.middleware("http")
async def count_requests(request: Request, call_next):
    state.request_count += 1
    response = await call_next(request)
    if response.status_code >= 400:
        state.error_count += 1
        state.last_errors.append({
            "time": datetime.datetime.now().isoformat(),
            "path": request.url.path,
            "status": response.status_code
        })
        state.last_errors = state.last_errors[-10:]
    return response

@app.middleware("http")
async def log_requests_to_dashboard(request: Request, call_next):
    """Middleware to log all requests to the dashboard stream"""
    start_time = time.time()
    response = await call_next(request)
    duration = round(time.time() - start_time, 3)
    log_msg = f"{request.method} {request.url.path} | Status: {response.status_code} | {duration}s"
    add_log(log_msg)
    return response

@app.get("/api/health")
async def health_check():
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    
    main_api_requests = 0
    try:
        main_req = redis_client.get("stats:main_api:total_requests")
        if main_req:
            main_api_requests = int(main_req)
    except:
        pass
    
    redis_ok = False
    redis_info = {}
    try:
        redis_ok = redis_client.ping()
        redis_info = redis_client.info("server")
    except:
        pass
    
    active_sessions = 0
    try:
        sessions = redis_client.keys("user:*:api_key")
        active_sessions = len(sessions)
    except:
        pass
    
    uptime = datetime.datetime.now() - state.start_time if state.start_time else "0"
    
    add_log(f"Health check | Main API: {main_api_requests} | Sessions: {active_sessions}")
    
    return {
        "status": state.status,
        "uptime": str(uptime).split('.')[0],
        "engine": "Singleton-V2",
        "timestamp": datetime.datetime.now().isoformat(),
        "metrics": {
            "total_requests": state.request_count,
            "total_errors": state.error_count,
            "active_sessions": active_sessions,
            "cpu_percent": cpu_percent,
            "main_api_requests": main_api_requests,
            "memory_used_mb": round(memory.used / 1024 / 1024, 2),
            "memory_total_mb": round(memory.total / 1024 / 1024, 2),
            "memory_percent": memory.percent
        },
        "redis": {
            "connected": redis_ok,
            "version": redis_info.get("redis_version", "unknown") if redis_ok else "disconnected"
        }
    }

@app.get("/api/stream-logs")
async def stream_logs():
    """Server-Sent Events stream for live logs"""
    async def event_generator():
        last_index = 0
        while True:
            if len(logs_cache) > last_index:
                for i in range(last_index, len(logs_cache)):
                    yield f"data: {logs_cache[i]}\n\n"
                last_index = len(logs_cache)
            await asyncio.sleep(0.5)
    
    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.get("/", response_class=HTMLResponse)
async def root():
    uptime = datetime.datetime.now() - state.start_time if state.start_time else "0"
    uptime_str = str(uptime).split('.')[0]
    
    cpu_percent = psutil.cpu_percent(interval=0.5)
    memory = psutil.virtual_memory()
    
    redis_ok = False
    try:
        redis_ok = redis_client.ping()
    except:
        pass
    
    active_sessions = 0
    try:
        sessions = redis_client.keys("user:*:api_key")
        active_sessions = len(sessions)
    except:
        pass
    
    main_api_requests = 0
    try:
        main_req = redis_client.get("stats:main_api:total_requests")
        if main_req:
            main_api_requests = int(main_req)
    except:
        pass
    
    total_req = f"{state.request_count:,}"
    main_api_fmt = f"{main_api_requests:,}"
    
    # Add a test log to verify streaming works
    add_log(f"Dashboard viewed - Main API: {main_api_fmt}")

    html = f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Nova Thor Engine | System Status</title>
        <style>
            :root {{
                --primary: #3b82f6;
                --success: #10b981;
                --warning: #f59e0b;
                --danger: #ef4444;
                --dark: #111827;
                --light: #f9fafb;
                --gray: #6b7280;
            }}
            
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
                background: linear-gradient(135deg, #111827 0%, #1f2937 100%);
                color: white;
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 20px;
            }}
            
            .dashboard {{
                max-width: 1200px;
                width: 100%;
            }}
            
            .header {{
                text-align: center;
                margin-bottom: 40px;
            }}
            
            .header h1 {{
                font-size: 3rem;
                background: linear-gradient(135deg, #3b82f6, #10b981);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin-bottom: 10px;
            }}
            
            .badge {{
                display: inline-block;
                padding: 8px 16px;
                border-radius: 9999px;
                font-weight: 600;
                font-size: 0.875rem;
                margin: 0 5px;
            }}
            
            .badge-success {{
                background: #10b98120;
                color: #10b981;
                border: 1px solid #10b98140;
            }}
            
            .badge-primary {{
                background: #3b82f620;
                color: #3b82f6;
                border: 1px solid #3b82f640;
            }}
            
            .grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }}
            
            .card {{
                background: #1f2937;
                border-radius: 15px;
                padding: 25px;
                border: 1px solid #374151;
                transition: transform 0.3s, box-shadow 0.3s;
            }}
            
            .card:hover {{
                transform: translateY(-2px);
                box-shadow: 0 10px 40px rgba(59, 130, 246, 0.1);
            }}
            
            .card-title {{
                color: var(--gray);
                font-size: 0.875rem;
                text-transform: uppercase;
                letter-spacing: 0.05em;
                margin-bottom: 10px;
            }}
            
            .card-value {{
                font-size: 2.5rem;
                font-weight: bold;
                margin-bottom: 5px;
            }}
            
            .card-label {{
                color: var(--gray);
                font-size: 0.875rem;
            }}
            
            .status-bar {{
                height: 8px;
                background: #374151;
                border-radius: 4px;
                overflow: hidden;
                margin: 15px 0;
            }}
            
            .status-fill {{
                height: 100%;
                background: linear-gradient(90deg, #3b82f6, #10b981);
                border-radius: 4px;
                width: 0%;
                transition: width 0.3s;
            }}
            
            .stats-grid {{
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 15px;
                margin-top: 20px;
            }}
            
            .stat-item {{
                background: #111827;
                padding: 15px;
                border-radius: 10px;
                text-align: center;
            }}
            
            .stat-value {{
                font-size: 1.5rem;
                font-weight: bold;
                color: #3b82f6;
            }}
            
            .stat-label {{
                color: var(--gray);
                font-size: 0.75rem;
                margin-top: 5px;
            }}
            
            .broker-badge {{
                background: #10b98120;
                color: #10b981;
                padding: 4px 12px;
                border-radius: 9999px;
                font-size: 0.875rem;
                border: 1px solid #10b98140;
                display: inline-block;
            }}
            
            .highlight {{
                color: var(--primary);
                font-size: 3.5rem;
                font-weight: bold;
            }}
            
            .footer {{
                text-align: center;
                margin-top: 40px;
                color: var(--gray);
                font-size: 0.875rem;
            }}
            
            .endpoint-list {{
                list-style: none;
                margin-top: 15px;
            }}
            
            .endpoint-list li {{
                padding: 8px 0;
                border-bottom: 1px solid #374151;
                display: flex;
                justify-content: space-between;
                color: #9ca3af;
            }}
            
            .endpoint-list li span:first-child {{
                color: white;
            }}
            
            .log-container {{
                background: #0a0a0a;
                color: #00ff00;
                padding: 15px;
                border-radius: 10px;
                font-family: 'Courier New', monospace;
                height: 200px;
                overflow-y: auto;
                border: 1px solid #333;
                margin-top: 20px;
                font-size: 0.9rem;
                box-shadow: inset 0 0 10px rgba(0,0,0,0.5);
            }}
            
            .log-container div {{
                border-bottom: 1px solid #1a1a1a;
                padding: 2px 0;
            }}
            
            .log-title {{
                color: var(--primary);
                font-size: 1rem;
                margin-bottom: 10px;
                display: flex;
                align-items: center;
                gap: 10px;
            }}
            
            .live-indicator {{
                display: inline-block;
                width: 10px;
                height: 10px;
                background-color: #ef4444;
                border-radius: 50%;
                animation: pulse 1.5s infinite;
            }}
            
            @keyframes pulse {{
                0% {{ opacity: 1; }}
                50% {{ opacity: 0.3; }}
                100% {{ opacity: 1; }}
            }}
        </style>
    </head>
    <body>
        <div class="dashboard">
            <div class="header">
                <h1>⚡ NOVA THOR ENGINE</h1>
                <div style="margin-top: 15px;">
                    <span class="badge badge-success">🟢 Operational</span>
                    <span class="badge badge-primary">Kr000820</span>
                    <span class="badge badge-primary">127146</span>
                </div>
                <p style="color: var(--gray); margin-top: 15px;">
                    Uptime: {uptime_str} • Last checked: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                </p>
            </div>

            <div class="grid">
                <div class="card">
                    <div class="card-title">Main API Requests</div>
                    <div class="highlight">{main_api_fmt}</div>
                    <div class="card-label">Total API calls to port 8080</div>
                </div>
                <div class="card">
                    <div class="card-title">Singleton Requests</div>
                    <div class="card-value">{total_req}</div>
                    <div class="card-label">Calls to this dashboard</div>
                </div>
                <div class="card">
                    <div class="card-title">Active Sessions</div>
                    <div class="card-value">{active_sessions}</div>
                    <div class="card-label">Connected users</div>
                    <div style="margin-top: 20px;">
                        <span class="broker-badge">Redis: {'✅ Connected' if redis_ok else '❌ Disconnected'}</span>
                    </div>
                </div>
            </div>

            <div class="grid">
                <div class="card">
                    <div class="card-title">System Resources</div>
                    <div style="margin-bottom: 15px;">
                        <span style="color: var(--primary); font-size: 1.2rem;">CPU: {cpu_percent:.1f}%</span>
                    </div>
                    <div class="status-bar">
                        <div class="status-fill" style="width: {cpu_percent}%;"></div>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin: 10px 0;">
                        <span>RAM: {memory.percent:.1f}%</span>
                        <span>{memory.used / 1024 / 1024 / 1024:.1f}GB / {memory.total / 1024 / 1024 / 1024:.1f}GB</span>
                    </div>
                    <div class="status-bar">
                        <div class="status-fill" style="width: {memory.percent}%; background: linear-gradient(90deg, #10b981, #3b82f6);"></div>
                    </div>
                </div>
                <div class="card">
                    <div class="card-title">Recent Errors</div>
                    <ul class="endpoint-list">
                        {''.join([f'<li><span>{e["path"]}</span> <span style="color: #ef4444;">{e["status"]}</span></li>' for e in state.last_errors]) if state.last_errors else '<li style="color: #10b981;">✓ No recent errors</li>'}
                    </ul>
                </div>
            </div>

            <!-- LIVE LOG WINDOW -->
            <div style="margin-top: 20px;">
                <div class="log-title">
                    <span class="live-indicator"></span>
                    <span>LIVE ACTIVITY STREAM</span>
                </div>
                <div class="log-container" id="log-window">
                    <div>Connecting to Thor Engine...</div>
                </div>
            </div>

            <div class="footer">
                <p>Nova Global Keys • Broker: Kr000820 • Affiliate: 127146</p>
                <p style="margin-top: 10px;">Built in Pakistan • Running global • Enterprise Grade</p>
            </div>
        </div>

<script>
    const evtSource = new EventSource("/api/stream-logs");
    const logWindow = document.getElementById("log-window");

    evtSource.onmessage = function(event) {{
        const newElement = document.createElement("div");
        newElement.textContent = event.data;
        logWindow.prepend(newElement);

        if (logWindow.children.length > 30) {{
            logWindow.removeChild(logWindow.lastChild);
        }}
    }};

    evtSource.onerror = function() {{
        console.log("EventSource error - reconnecting...");
    }};
</script>
    </body>
    </html>
    '''
    return HTMLResponse(content=html)

@app.get("/api/health/json")
async def health_json():
    return await health_check()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8081))
    uvicorn.run(app, host="0.0.0.0", port=port)
