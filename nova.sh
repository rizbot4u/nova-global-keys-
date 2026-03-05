#!/bin/bash

case "$1" in
  status)
    /root/nova-global-keys-/status_complete.sh
    ;;
  start)
    cd /root/nova-global-keys-/services
    pm2 start auth/main.py --name nova-auth --interpreter python3
    pm2 start user/main.py --name nova-user --interpreter python3
    pm2 start market/main.py --name nova-market --interpreter python3
    pm2 start trade/main.py --name nova-trade --interpreter python3
    pm2 start p2p/main.py --name nova-p2p --interpreter python3
    pm2 start broker/main.py --name nova-broker --interpreter python3
    pm2 start gateway/main.py --name nova-gateway --interpreter python3
    pm2 start telegram/main.py --name nova-telegram --interpreter python3
    cd /root/nova-global-keys-/frontend
    pm2 start npm --name nova-frontend -- run start
    echo "✅ All services started!"
    ;;
  stop)
    pm2 stop all
    echo "✅ All services stopped!"
    ;;
  restart)
    pm2 restart all
    echo "✅ All services restarted!"
    ;;
  logs)
    pm2 logs
    ;;
  *)
    echo "Usage: ./nova.sh {status|start|stop|restart|logs}"
    ;;
esac
