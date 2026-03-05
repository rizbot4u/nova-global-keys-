module.exports = {
  apps: [
    {
      name: 'nova-auth',
      cwd: '/root/nova-global-keys-/services',
      script: '/root/nova-global-keys-/venv/bin/uvicorn',
      args: 'auth.main:app --host 127.0.0.1 --port 8001',
      interpreter: 'none',
      env: {
        PYTHONPATH: '/root/nova-global-keys-/services'
      }
    },
    {
      name: 'nova-user',
      cwd: '/root/nova-global-keys-/services',
      script: '/root/nova-global-keys-/venv/bin/uvicorn',
      args: 'user.main:app --host 127.0.0.1 --port 8002',
      interpreter: 'none',
      env: {
        PYTHONPATH: '/root/nova-global-keys-/services'
      }
    },
    {
      name: 'nova-market',
      cwd: '/root/nova-global-keys-/services',
      script: '/root/nova-global-keys-/venv/bin/uvicorn',
      args: 'market.main:app --host 127.0.0.1 --port 8003',
      interpreter: 'none',
      env: {
        PYTHONPATH: '/root/nova-global-keys-/services'
      }
    },
    {
      name: 'nova-trade',
      cwd: '/root/nova-global-keys-/services',
      script: '/root/nova-global-keys-/venv/bin/uvicorn',
      args: 'trade.main:app --host 127.0.0.1 --port 8004',
      interpreter: 'none',
      env: {
        PYTHONPATH: '/root/nova-global-keys-/services'
      }
    },
    {
      name: 'nova-p2p',
      cwd: '/root/nova-global-keys-/services',
      script: '/root/nova-global-keys-/venv/bin/uvicorn',
      args: 'p2p.main:app --host 127.0.0.1 --port 8005',
      interpreter: 'none',
      env: {
        PYTHONPATH: '/root/nova-global-keys-/services'
      }
    },
    {
      name: 'nova-broker',
      cwd: '/root/nova-global-keys-/services',
      script: '/root/nova-global-keys-/venv/bin/uvicorn',
      args: 'broker.main:app --host 127.0.0.1 --port 8006',
      interpreter: 'none',
      env: {
        PYTHONPATH: '/root/nova-global-keys-/services'
      }
    },
    {
      name: 'nova-gateway',
      cwd: '/root/nova-global-keys-/services',
      script: '/root/nova-global-keys-/venv/bin/uvicorn',
      args: 'gateway.main:app --host 127.0.0.1 --port 8081',
      interpreter: 'none',
      env: {
        PYTHONPATH: '/root/nova-global-keys-/services'
      }
    },
    {
      name: 'nova-telegram',
      cwd: '/root/nova-global-keys-/bot',
      script: '/root/nova-global-keys-/venv/bin/python',
      args: 'telegram_bot.py',
      interpreter: 'none',
      env: {
        PYTHONPATH: '/root/nova-global-keys-/services'
      }
    }
  ]
}
