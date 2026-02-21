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
    }
  ]
};
