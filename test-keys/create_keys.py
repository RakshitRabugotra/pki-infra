import rsa

NO_BITS = 1024

username = input("Enter your username: ")

# Generate RSA key pair
(public_key, private_key) = rsa.newkeys(NO_BITS)

# Export private key in PKCS#1 format
private_key_pem = private_key.save_pkcs1(format='PEM')
with open(f"{username}-private_key.pem", "wb") as priv_file:
    priv_file.write(private_key_pem)

# Export public key in PKCS#1 format
public_key_pem = public_key.save_pkcs1(format='PEM')
with open(f"{username}-public_key.pem", "wb") as pub_file:
    pub_file.write(public_key_pem)