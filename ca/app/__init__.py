from flask import Flask, request, jsonify, render_template
import json
import time
import os

# Custom modules
from app.lib.crypt import Certificate, register_certificate, is_revoked, sign, verify
from app.lib.mail import mail_service
from app.lib.util import timestamp
from app.constants import CERTIFICATE_DIR

app = Flask(__name__)

# Simulated databases
REQUEST_LIMIT = 5
certificate_requests: list[Certificate] = []  # Store requests from RA for CA approval

issued_certificates = {}  # Store issued certificates by public key
crl = set()  # Set of revoked certificate IDs


@app.route("/")
def home():
    global certificate_requests
    return render_template("index.html", requests=certificate_requests)


@app.route("/ca/request_approval", methods=["POST"])
def request_approval():
    # If the request queue is full, then return busy status
    if len(certificate_requests) >= REQUEST_LIMIT:
        return (
            jsonify(
                {
                    "status": "request queue full",
                    "message": "The server is busy, try again later",
                }
            ),
            503,
        )

    # Get the details of the certificate from the request
    data = request.get_json()
    public_key: str = data.get("public_key")
    identifier: str = data.get("identifier")
    request_id: str = data.get("request_id")

    # Simulate certificate signing
    certificate = Certificate.from_dict(
        {
            "request_id": request_id,
            "public_key": public_key,
            "identifier": identifier,
            "issued_by": None,
            "issued_at": None,
            "certificate_id": None,
            "sign": None,
        }
    )

    # Append this request to the queue
    certificate_requests.append(certificate)

    return (
        jsonify(
            {
                "status": "request queued",
                "message": "The request for certificate has been queued",
            }
        ),
        200,
    )


@app.route("/ca/approve_request/<string:request_id>", methods=["GET"])
def approve_request(request_id: str):
    global certificate_requests
    # Get the matching certificate from the list
    # Check if the id is valid and exists in pending requests
    request_matches: list[Certificate] = list(
        filter(lambda request: request.request_id == request_id, certificate_requests)
    )
    certificate: Certificate = None
    try:
        assert len(request_matches) == 1
        certificate = request_matches[0]
        assert certificate is not None
    except AssertionError:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": f"The request with id: '{request_id}' doesn't exist",
                }
            ),
            404,
        )

    # Check if the certificate is revoked?
    if is_revoked(certificate):
        return (
            jsonify({"message": "The certificate is revoked", "status": "revoked"}),
            409,
        )

    try:
        certificate = Certificate(
            request_id=certificate.request_id,
            public_key=certificate.public_key,
            identifier=certificate.identifier,
            issued_by="CA",
            issued_at=time.time(),
            certificate_id=f"{certificate.identifier}-{int(time.time())}",
            sign=sign(certificate.public_key.encode()),
        )
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

    # Save the certificate
    register_certificate(certificate)
    
    # Create the certificate json and send the mail to the user
    file_path = os.path.join(CERTIFICATE_DIR, certificate.identifier + '.json')
    with open(file_path, mode="w+") as wFile:
        json.dump(certificate.to_dict(), wFile)
    
    # Create the certificate .pem file and attach it to the mail
    pem_file_path = os.path.join(CERTIFICATE_DIR, certificate.identifier.replace('.', '-') + '.pem')
    with open(pem_file_path, mode='w+') as wFile:
        wFile.write(certificate.public_key)

    try:
        # assuming that the identity is their email address
        mail_service.send_mail(
            "Public-Key Certificate", certificate.identifier, file_paths=[file_path, pem_file_path]
        )

        # Remove the certificate from the queue
        certificate_requests = list(
            filter(
                lambda cert: cert.request_id != certificate.request_id, certificate_requests
            )
        )

        # Return the certificate (simulate sending to the end-user via RA)
        return (
            jsonify(
                {
                    "certificate": certificate.to_dict(),
                    "status": "generated",
                    "message": "Certificate issued successfully.",
                }
            ),
            200,
        )

    except Exception as e:
        return (
            jsonify(
                {"status": "error", "message": "Error while sending the certificate " + str(e)}
            ),
            500,
        )


@app.route("/ca/verify_certificate", methods=["POST"])
def verify_certificate():
    public_key_file: bytes = request.files["public-key"]
    sign: str = request.form["sign"]

    # Save the file to the resource, TODO: can be optimized
    filename = os.path.join(CERTIFICATE_DIR, timestamp())
    public_key_file.save(filename)
    public_key = ""
    with open(filename, mode='r') as key_file:
        public_key = key_file.read()
    # Delete the file
    os.remove(filename)

    # Verify if certificate exists
    try:
        is_valid = verify(public_key.encode(), bytes.fromhex(sign))

        if is_valid:
            # # Simulate checking if the certificate is in the CRL (revoked)
            # if not is_revoked(public_key):
            #     return (
            #         jsonify({"status": "invalid", "message": "Certificate is revoked."}),
            #         400,
            #     )
            return jsonify({"status": "valid"}), 200
        else:
            return jsonify({"status": "invalid", "message": "Certificate not found."}), 400
    except Exception as e:
        return jsonify({"status": "invalid", "message": "Certificate is invalid: " + str(e)}), 400


@app.route("/ca/revoke_certificate/<certificate_id>", methods=["POST"])
def revoke_certificate(certificate_id):
    # Add to CRL (revocation list)
    crl.add(certificate_id)
    return (
        jsonify({"status": "revoked", "message": "Certificate revoked successfully."}),
        200,
    )
