#!/bin/bash
cd /root/nova-global-keys-
source venv/bin/activate
export PYTHONPATH=/root/nova-global-keys-:$PYTHONPATH
python3 workers/strategy_runner.py
