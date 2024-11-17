from flask import Flask, request, jsonify, render_template
import requests
import os

from app.constants import RESOURCE_DIR
from app.lib.util import timestamp, get_id

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Simulated database for storing requests
pending_requests = []  # Store requests for certificate verification

@app.route('/')
def home():
    global pending_requests
    return render_template('index.html', requests=pending_requests)

@app.route('/ra/request_certificate', methods=['POST'])
def request_certificate():
    public_key_file = request.files['public-key']
    identifier = request.form['identifier']

    # Save the file to the resource
    filename = os.path.join(RESOURCE_DIR, identifier + '-' + timestamp())
    public_key_file.save(filename)
    public_key = ""
    with open(filename, mode='r') as key_file:
        public_key = key_file.read()
    
    if not public_key or not identifier:
        return jsonify({"status": "error", "message": "Public key or identifier missing."}), 400
    
    # Create a simulated request and add it to the pending list
    request_data = {
        'public_key': public_key,
        'identifier': identifier,
        'status': 'pending',
        'request_id': get_id()
    }
    pending_requests.append(request_data)

    # Delete all the resources, like the file-contents of this id
    contents = filter(lambda file: file.startswith(identifier), os.listdir(RESOURCE_DIR))
    for content in contents:
        os.remove(os.path.join(RESOURCE_DIR, content))

    return jsonify({"status": "request_queued", "message": "Request has been queued for examination"}), 200

@app.route("/ra/forward_request/<string:request_id>", methods=['GET'])
def forward_request(request_id: str):

    # Check if the id is valid and exists in pending requests
    request_matches = list(filter(lambda request: request['request_id'] == request_id, pending_requests))
    request_data = None
    try:
        assert len(request_matches) == 1
        request_data = request_matches[0]
        assert request_data is not None
    except AssertionError:
        return jsonify({"status": "error", "message": f"The request with id: '{request_id}' doesn\'t exist"}), 404

    # Send the request to CA for certificate issuance
    ca_url = 'http://localhost:5001/ca/request_approval'
    response = requests.post(ca_url, json=request_data)
    
    if response.status_code == 200:
        # Remove the request from the list
        pending_requests = list(filter(lambda request: request['request_id'] != request_id, pending_requests))
        return jsonify({"status": "request_sent", "message": "Request sent to CA."}), 200
    else:
        return jsonify({"status": "error", "message": "Failed to forward request to CA."}), 400


@app.route('/ra/verify_certificate', methods=['POST'])
def verify_certificate():
    public_key = request.form['file']
    sign = request.form['sign']
    # Send the verification request to CA
    ca_url = 'http://localhost:5001/ca/verify_certificate'
    response = requests.post(ca_url, json={"public_key": public_key, 'sign': sign})
    
    return jsonify(response.json()), response.status_code
