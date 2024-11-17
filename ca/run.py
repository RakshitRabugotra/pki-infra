from flask import Flask, request, jsonify, render_template
import time

app = Flask(__name__)

# Simulated databases
certificate_requests = []  # Store requests from RA for CA approval
issued_certificates = {}  # Store issued certificates by public key
crl = set()  # Set of revoked certificate IDs

# Sample private key (just for simulation, real use would involve a private key)
CA_PRIVATE_KEY = "CA_PRIVATE_KEY_SIMULATED"

# Simulated certificate request (you could populate this with actual data from RA server)
certificate_requests = [
    {"public_key": "user_public_key_1", "identifier": "user1@example.com", "status": "pending", "request_id": 0},
    {"public_key": "user_public_key_2", "identifier": "user2@example.com", "status": "pending", "request_id": 1},
]

@app.route('/')
def home():
    return render_template('ca.html', requests=certificate_requests)

@app.route('/ca/approve_request/<int:req_id>', methods=['POST'])
def approve_request(req_id):
    # Find the request
    request_data = certificate_requests[req_id]
    public_key = request_data['public_key']
    identifier = request_data['identifier']
    
    # Simulate certificate signing
    certificate = {
        'public_key': public_key,
        'identifier': identifier,
        'issued_by': 'CA',
        'issued_at': time.time(),
        'certificate_id': f'{identifier}-{int(time.time())}'
    }
    
    # Save the certificate
    issued_certificates[public_key] = certificate
    certificate_requests.pop(req_id)
    
    # Return the certificate (simulate sending to the end-user via RA)
    return jsonify({"certificate": certificate, "status": "generated", "message": "Certificate issued successfully."}), 200

@app.route('/ca/verify_certificate', methods=['POST'])
def verify_certificate():
    data = request.get_json()
    public_key = data['public_key']
    
    # Verify if certificate exists
    certificate = issued_certificates.get(public_key)
    
    if certificate:
        # Simulate checking if the certificate is in the CRL (revoked)
        if certificate['certificate_id'] in crl:
            return jsonify({"status": "invalid", "message": "Certificate is revoked."}), 400
        
        return jsonify({"status": "valid", "certificate": certificate}), 200
    else:
        return jsonify({"status": "invalid", "message": "Certificate not found."}), 400

@app.route('/ca/revoke_certificate/<certificate_id>', methods=['POST'])
def revoke_certificate(certificate_id):
    # Add to CRL (revocation list)
    crl.add(certificate_id)
    return jsonify({"status": "revoked", "message": "Certificate revoked successfully."}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5001)  # CA server running on port 5001
