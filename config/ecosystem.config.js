module.exports = {
  apps: [
    {
      name: "nova-thor",
      script: "thor_engine.py",
      interpreter: "/root/nova-global-keys-/venv/bin/python3",
      cwd: "/root/nova-global-keys-",
      autorestart: true,
      watch: false,
      max_restarts: 10,
      min_uptime: "10s",
      env: {
        NODE_ENV: "production",
        PYTHONUNBUFFERED: "1",
        PYTHONPATH: "/root/nova-global-keys-"
      },
      error_file: "/root/nova-global-keys-/logs/thor-error.log",
      out_file: "/root/nova-global-keys-/logs/thor-out.log"
    },
    {
      name: "thor-singleton",
      script: "thor_v2.py",
      interpreter: "/root/nova-global-keys-/venv/bin/python3",
      cwd: "/root/nova-global-keys-",
      autorestart: true,
      watch: false,
      env: {
        PYTHONPATH: "/root/nova-global-keys-"
      },
      error_file: "/root/nova-global-keys-/logs/singleton-error.log",
      out_file: "/root/nova-global-keys-/logs/singleton-out.log"
    }
  ]
}
