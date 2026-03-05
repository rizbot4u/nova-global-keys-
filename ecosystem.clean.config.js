module.exports = {
  apps: [
    {
      name: 'nova-auth',
      cwd: '/root/nova-global-keys-/services',
      script: 'auth/main.py',
      interpreter: 'python3',
      watch: false,
      max_memory_restart: '500M'
    },
    {
      name: 'nova-user',
      cwd: '/root/nova-global-keys-/services',
      script: 'user/main.py',
      interpreter: 'python3',
      watch: false
    },
    {
      name: 'nova-market',
      cwd: '/root/nova-global-keys-/services',
      script: 'market/main.py',
      interpreter: 'python3',
      watch: false
    },
    {
      name: 'nova-trade',
      cwd: '/root/nova-global-keys-/services',
      script: 'trade/main.py',
      interpreter: 'python3',
      watch: false
    },
    {
      name: 'nova-p2p',
      cwd: '/root/nova-global-keys-/services',
      script: 'p2p/main.py',
      interpreter: 'python3',
      watch: false
    },
    {
      name: 'nova-broker',
      cwd: '/root/nova-global-keys-/services',
      script: 'broker/main.py',
      interpreter: 'python3',
      watch: false
    },
    {
      name: 'nova-gateway',
      cwd: '/root/nova-global-keys-/services',
      script: 'gateway/main.py',
      interpreter: 'python3',
      watch: false
    },
    {
      name: 'nova-telegram',
      cwd: '/root/nova-global-keys-/bot',
      script: 'stable_telegram.py',
      interpreter: 'python3',
      watch: false,
      max_restarts: 10,
      min_uptime: '10s'
    }
  ]
}
