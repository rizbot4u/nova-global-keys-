#!/bin/bash
cd /root/nova-global-keys-
export PYTHONPATH=/root/nova-global-keys-:$PYTHONPATH
python3 social_bot/social_manager.py
