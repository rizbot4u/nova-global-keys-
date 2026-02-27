module.exports = {
  apps: [
    {
      name: "nova-thor",
      script: "thor_engine.py",
      interpreter: "python3",
      cwd: "/srv/nova-global-keys",
      autorestart: true,
      watch: false,
      max_restarts: 10,
      min_uptime: "10s",
      env: {
        NODE_ENV: "production",
        PYTHONUNBUFFERED: "1"
      },
      error_file: "/srv/nova-global-keys/logs/thor-error.log",
      out_file: "/srv/nova-global-keys/logs/thor-out.log"
    },
    {
      name: "nova-worker",
      script: "workers/strategy_runner.py",
      interpreter: "python3",
      cwd: "/srv/nova-global-keys",
      autorestart: true,
      watch: false,
      max_restarts: 10,
      min_uptime: "10s",
      env: {
        NODE_ENV: "production",
        PYTHONUNBUFFERED: "1"
      },
      error_file: "/srv/nova-global-keys/logs/worker-error.log",
      out_file: "/srv/nova-global-keys/logs/worker-out.log"
    },
    {
      name: "nova-signal",
      script: "/srv/nova-global-keys/signals/signal_bot.py",
      interpreter: "/srv/nova/prod/venv/bin/python3",
      cwd: "/srv/nova-global-keys",
      autorestart: true,
      watch: false,
      max_restarts: 10,
      min_uptime: "10s",
      env: {
        NODE_ENV: "production",
        PYTHONUNBUFFERED: "1"
      },
      error_file: "/srv/nova-global-keys/logs/signal-error.log",
      out_file: "/srv/nova-global-keys/logs/signal-out.log"
    }
  ]
};
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
    }  // ← NO COMMA HERE!
  ]
};
