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

# Step 3: Verify certificate by contacting CA server
echo "Step 3: Verifying certificate with CA server..."

verification_response=$(curl -s -X POST http://localhost:5001/ca/verify_certificate \
    -H "Content-Type: application/json" \
    -d '{
          "public_key": "user_public_key_1234"
        }')

# Display the verification response from CA
echo "CA Response: $verification_response"

# Check if the certificate is valid
if [[ "$verification_response" == *"valid"* ]]; then
    echo "Certificate is valid. Certificate details:"
    echo "$verification_response"
else
    echo "Error: Certificate verification failed."
    exit 1
fi
