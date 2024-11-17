from flask import Flask, request, jsonify, render_template
import requests

app = Flask(__name__)

# Simulated database for storing requests
pending_requests = []  # Store requests for certificate verification

@app.route('/')
def home():
    return render_template('ra.html', requests=pending_requests)

@app.route('/ra/request_certificate', methods=['POST'])
def request_certificate():
    data = request.get_json()
    public_key = data.get('public_key')
    identifier = data.get('identifier')
    
    if not public_key or not identifier:
        return jsonify({"status": "error", "message": "Public key or identifier missing."}), 400
    
    # Create a simulated request and add it to the pending list
    request_data = {
        'public_key': public_key,
        'identifier': identifier,
        'status': 'pending',
        'request_id': len(pending_requests)
    }
    pending_requests.append(request_data)
    
    # Send the request to CA for certificate issuance
    ca_url = 'http://localhost:5001/ca/approve_request/{}'.format(len(pending_requests) - 1)
    response = requests.post(ca_url)
    
    if response.status_code == 200:
        return jsonify({"status": "request_sent", "message": "Request sent to CA."}), 200
    else:
        return jsonify({"status": "error", "message": "Failed to forward request to CA."}), 400

@app.route('/ra/verify_certificate', methods=['POST'])
def verify_certificate():
    data = request.get_json()
    public_key = data.get('public_key')
    
    # Send the verification request to CA
    ca_url = 'http://localhost:5001/ca/verify_certificate'
    response = requests.post(ca_url, json={"public_key": public_key})
    
    return jsonify(response.json()), response.status_code

if __name__ == '__main__':
    app.run(debug=True, port=5000)  # RA server running on port 5000
