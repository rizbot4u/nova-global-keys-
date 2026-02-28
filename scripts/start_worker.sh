#!/bin/bash
# Start the strategy worker in background
cd /srv/nova-global-keys
source venv/bin/activate
python -m workers.strategy_runner
