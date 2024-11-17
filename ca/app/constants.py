import os

# Directory paths
RESOURCE_DIR = os.path.join("app", "static", "res")
CERTIFICATE_DIR = os.path.join(RESOURCE_DIR, "certificates")

# File paths
CRL_FILE = os.path.join(RESOURCE_DIR, "crl.csv")
RECORD_FILE = os.path.join(RESOURCE_DIR, 'records.csv')


# Create the directory, if doesn't exist
if not os.path.isdir(RESOURCE_DIR):
    os.mkdir(RESOURCE_DIR)
if not os.path.isdir(CERTIFICATE_DIR):
    os.mkdir(CERTIFICATE_DIR)