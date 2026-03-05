module.exports = {
  apps: [{
    name: 'nova-thor-engine',
    script: 'thor_engine.py',
    interpreter: 'python3',
    watch: false,
    max_memory_restart: '500M',
    log_file: './logs/thor-engine.log',
    error_file: './logs/thor-engine-error.log',
    out_file: './logs/thor-engine-out.log',
    time: true,
    autorestart: true,
    restart_delay: 5000,
    max_restarts: 10,
    env: {
      PYTHONUNBUFFERED: '1',
      PORT: '8081'  // Change port to avoid conflict
    }
  }]
}
