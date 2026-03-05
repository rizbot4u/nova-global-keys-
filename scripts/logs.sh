#!/bin/bash

if [ -z "$1" ]; then
    echo "Usage: ./logs.sh [service]"
    echo "Services: gateway, auth, user, market, trade, p2p, broker, telegram, all"
    exit 1
fi

case $1 in
    gateway)
        tail -f /root/nova-global-keys-/logs/gateway/gateway.log
        ;;
    auth)
        tail -f /root/nova-global-keys-/logs/auth/auth.log
        ;;
    user)
        tail -f /root/nova-global-keys-/logs/user/user.log
        ;;
    market)
        tail -f /root/nova-global-keys-/logs/market/market.log
        ;;
    trade)
        tail -f /root/nova-global-keys-/logs/trade/trade.log
        ;;
    p2p)
        tail -f /root/nova-global-keys-/logs/p2p/p2p.log
        ;;
    broker)
        tail -f /root/nova-global-keys-/logs/broker/broker.log
        ;;
    telegram)
        tail -f /root/nova-global-keys-/logs/telegram.log
        ;;
    all)
        tail -f /root/nova-global-keys-/logs/*/*.log
        ;;
    *)
        echo "Unknown service: $1"
        exit 1
        ;;
esac
