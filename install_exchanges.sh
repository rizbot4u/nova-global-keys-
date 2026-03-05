#!/bin/bash

echo "📦 Installing exchange dependencies..."

# Activate virtual environment
source /root/nova-global-keys-/venv/bin/activate

# Install exchange libraries
pip install httpx==0.25.1
pip install python-binance==1.0.19
pip install kucoin-python==2.2.0

echo "✅ Exchange libraries installed!"
