module.exports = {
  apps: [
    {
      name: 'nova-auth',
      script: '/root/nova-global-keys-/services/auth/main.py',
      interpreter: 'python3',
      cwd: '/root/nova-global-keys-/services'
    },
    {
      name: 'nova-user',
      script: '/root/nova-global-keys-/services/user/main.py',
      interpreter: 'python3',
      cwd: '/root/nova-global-keys-/services'
    },
    {
      name: 'nova-market',
      script: '/root/nova-global-keys-/services/market/main.py',
      interpreter: 'python3',
      cwd: '/root/nova-global-keys-/services'
    },
    {
      name: 'nova-trade',
      script: '/root/nova-global-keys-/services/trade/main.py',
      interpreter: 'python3',
      cwd: '/root/nova-global-keys-/services'
    },
    {
      name: 'nova-p2p',
      script: '/root/nova-global-keys-/services/p2p/main.py',
      interpreter: 'python3',
      cwd: '/root/nova-global-keys-/services'
    },
    {
      name: 'nova-broker',
      script: '/root/nova-global-keys-/services/broker/main.py',
      interpreter: 'python3',
      cwd: '/root/nova-global-keys-/services'
    },
    {
      name: 'nova-gateway',
      script: '/root/nova-global-keys-/services/gateway/main.py',
      interpreter: 'python3',
      cwd: '/root/nova-global-keys-/services'
    },
    {
      name: 'nova-telegram',
      script: '/root/nova-global-keys-/services/telegram/main.py',
      interpreter: 'python3',
      cwd: '/root/nova-global-keys-/services/telegram'
    }
  ]
}
