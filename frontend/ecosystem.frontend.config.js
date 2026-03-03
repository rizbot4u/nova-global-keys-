module.exports = {
  apps: [{
    name: 'nova-frontend',
    cwd: '/root/nova-global-keys-/frontend',
    script: 'npm',
    args: 'start',
    interpreter: 'none',
    watch: false,
    max_memory_restart: '500M',
    log_file: './logs/frontend.log',
    error_file: './logs/frontend-error.log',
    out_file: './logs/frontend-out.log',
    time: true,
    autorestart: true,
    restart_delay: 5000,
    max_restarts: 10,
    env: {
      NODE_ENV: 'production',
      PORT: 3000
    }
  }]
}
