import base64
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    PrivateFormat,
    BestAvailableEncryption,
    PublicFormat,
    load_pem_public_key,
    load_pem_private_key
)
from cryptography.hazmat.primitives import hashes
from asymmetric.interface import AsymmetricEncryption


class RSA(AsymmetricEncryption):
    def generate_keys(self, pw: str, get_pw: bool = False):
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        public_key = private_key.public_key()

        private_key_pem = private_key.private_bytes(
            encoding=Encoding.PEM,
            format=PrivateFormat.PKCS8,
            encryption_algorithm=BestAvailableEncryption(pw.encode())
        ).decode()

        public_key_pem = public_key.public_bytes(
            encoding=Encoding.PEM,
            format=PublicFormat.SubjectPublicKeyInfo
        ).decode()

        if get_pw:
            return private_key_pem, public_key_pem, pw
        return private_key_pem, public_key_pem, None

    def encrypt(self, public_key_pem: str, plaintext: str):
        public_key = load_pem_public_key(public_key_pem.encode())
        ciphertext = public_key.encrypt(
            plaintext.encode(),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return base64.b64encode(ciphertext).decode('utf-8')

    def decrypt(self, private_key_pem: str, ciphertext: str, pw: str):
        private_key = load_pem_private_key(
            private_key_pem.encode(),
            password=pw.encode(),
            backend=None  # You might need to specify the backend or it can be default
        )
        plaintext = private_key.decrypt(
            base64.b64decode(ciphertext),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return plaintext.decode()
