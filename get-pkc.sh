#!/bin/bash

# Function to check if curl is installed
check_curl() {
    if ! command -v curl &> /dev/null
    then
        echo "curl could not be found. Please install curl to continue."
        exit 1
    fi
}

# Check if curl is installed
check_curl

echo "Step 1: Sending request to RA server to generate a PKC..."

# Step 1: Send request to RA server
response=$(curl -s -X POST http://localhost:5000/ra/request_certificate \
    -H "Content-Type: application/json" \
    -d '{
          "public_key": "user_public_key_1234",
          "identifier": "user@example.com"
        }')

# Display the response from RA
echo "RA Response: $response"

# Check if the RA response was successful
if [[ "$response" == *"Request sent to CA"* ]]; then
    echo "Request forwarded to CA successfully. RA Response: $response"
else
    echo "Error: Failed to forward request to CA. Exiting."
    exit 1
fi