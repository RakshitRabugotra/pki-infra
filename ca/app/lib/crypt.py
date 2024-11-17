import rsa
import csv
import os 

# Custom modules and libraries
from app.constants import RESOURCE_DIR, CRL_FILE, RECORD_FILE
from app.lib.types import Certificate

# Configuration for the keys generated
NO_BITS = 1024
PUBLIC_KEY = "public.pem"
PRIVATE_KEY = "private.pem"

# Configuration for the Digital Signature
SIGN_METHOD = "SHA-256"


def load_public_key():
    """
    Loads the RSA key-pair for this server, only public
    """
    public_key = None

    try:
        with open(os.path.join(RESOURCE_DIR, PUBLIC_KEY), mode='rb') as f:
            public_key = rsa.PublicKey.load_pkcs1(f.read())
        
    except Exception as e:
        print("[ERROR]: Error while reading public key: ", e)
        exit(-1)
    
    return public_key

            
def encrypt(message: str, public_key: rsa.PublicKey):
    """
    
    """
    return rsa.encrypt(message.encode('ascii'), public_key)

def decrypt(message: str, private_key: rsa.PrivateKey):
    """
    
    """
    return rsa.decrypt(message.encode('ascii'), private_key)


def sign(message: bytes, private_key: bytes=None, hash_method: str=SIGN_METHOD):
    # Get the private key of the server
    private_key = private_key or __load_private_key()
    return rsa.sign(message, private_key, hash_method)


def verify(message: str, signature: bytes, public_key: bytes):
    return rsa.verify(message.encode('ascii'), signature, rsa.PublicKey.load_pkcs1(public_key))

def register_certificate(certificate: Certificate):
    with open(RECORD_FILE, mode='a+') as file:
        writer = csv.DictWriter(file, delimiter=';', fieldnames=['id', 'public-key'])
        writer.writerow({
            'id': certificate.identifier,
            'public-key': certificate.public_key
        })
    return 0

def is_revoked(public_key: bytes):
    try:
        with open(CRL_FILE, mode='r+') as file:
            reader = csv.DictReader(file, delimiter=';')
            for record in reader:
                if record['public-key'] == public_key:
                    return True
    except FileNotFoundError:
        return False
    
    return False


def revoke_certificate(certificate: Certificate):
    with open(CRL_FILE, mode='a+') as file:
        writer = csv.DictWriter(file, delimiter=';', fieldnames=['id', 'public-key'])
        writer.writerow({
            "id": certificate.identifier,
            "public-key": certificate.public_key
        })
    return 0

"""
Private methods
"""

def __load_private_key():
    """
    Loads the RSA key-pair for this server, only private
    """
    private_key = None

    try:
        with open(os.path.join(RESOURCE_DIR, PRIVATE_KEY), mode='rb') as f:
            private_key = rsa.PrivateKey.load_pkcs1(f.read())
    except Exception as e:
        print("[ERROR]: Error while reading private key: ", e)
        exit(-1)
    
    return private_key


def __create_keys():
    print("[DEBUG]: Creating RSA key-pair")
    public_key, private_key = rsa.newkeys(NO_BITS)

    try:
        with open(os.path.join(RESOURCE_DIR, PUBLIC_KEY), mode='wb') as pub:
            pub.write(public_key.save_pkcs1("PEM"))
        
        with open(os.path.join(RESOURCE_DIR, PRIVATE_KEY), mode='wb') as priv:
            priv.write(private_key.save_pkcs1("PEM"))
    except Exception as e:
        print("[ERROR]: Error while generating keys: ", e)
        return -1

    return 0

# If the rsa files aren't defined, then create them
if not os.path.isfile(os.path.join(RESOURCE_DIR, PUBLIC_KEY)) \
    or not os.path.isfile(os.path.join(RESOURCE_DIR, PRIVATE_KEY)):
    # Create the keys
    status = __create_keys()
    try:
        # Check if the generation was succesful
        assert status == 0
    except AssertionError:
        exit(status)
    

    
        