{
  name: "nova-frontend",
  script: "npm",
  args: "start",
  cwd: "/root/nova-global-keys-/frontend",
  interpreter: "none",
  env: {
    NODE_ENV: "production",
    PORT: 3000
  },
  max_memory_restart: "300M",
  kill_timeout: 3000
}
