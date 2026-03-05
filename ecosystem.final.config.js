module.exports = {
  apps: [
    {
      name: 'nova-auth',
      cwd: '/root/nova-global-keys-/services',
      script: 'auth/main.py',
      interpreter: 'python3'
    },
    {
      name: 'nova-user',
      cwd: '/root/nova-global-keys-/services',
      script: 'user/main.py',
      interpreter: 'python3'
    },
    {
      name: 'nova-market',
      cwd: '/root/nova-global-keys-/services',
      script: 'market/main.py',
      interpreter: 'python3'
    },
    {
      name: 'nova-trade',
      cwd: '/root/nova-global-keys-/services',
      script: 'trade/main.py',
      interpreter: 'python3'
    },
    {
      name: 'nova-p2p',
      cwd: '/root/nova-global-keys-/services',
      script: 'p2p/main.py',
      interpreter: 'python3'
    },
    {
      name: 'nova-broker',
      cwd: '/root/nova-global-keys-/services',
      script: 'broker/main.py',
      interpreter: 'python3'
    },
    {
      name: 'nova-gateway',
      cwd: '/root/nova-global-keys-/services',
      script: 'gateway/main.py',
      interpreter: 'python3'
    },
    {
      name: 'nova-telegram',
      cwd: '/root/nova-global-keys-/services',
      script: 'telegram/service.py',
      interpreter: 'python3',
      watch: false
    }
  ]
}
