#!/bin/bash
cd /root/nova-global-keys-
export PYTHONPATH=/root/nova-global-keys-:$PYTHONPATH
python3 signals/signal_bot.py
