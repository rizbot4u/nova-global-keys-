#!/bin/bash

# Change these to your actual test credentials
EMAIL="admin@example.com"
PASSWORD="yourpassword"
LOGIN_URL="http://127.0.0.1:8081/api/auth/login"

echo "Attempting to login..."

# Capture the response
RESPONSE=$(curl -s -X POST "$LOGIN_URL" \
     -H "Content-Type: application/json" \
     -d "{\"email\": \"$EMAIL\", \"password\": \"$PASSWORD\"}")

# Extract the token (requires 'jq' to be installed)
TOKEN=$(echo $RESPONSE | jq -r '.access_token')

if [ "$TOKEN" != "null" ]; then
    echo "Login Successful!"
    echo "Your Token: ${TOKEN:0:15}..."
    echo $TOKEN > .token
else
    echo "Login Failed. Response:"
    echo $RESPONSE
fi
