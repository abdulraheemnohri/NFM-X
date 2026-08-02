from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.exceptions import InvalidSignature
from typing import Tuple
import base64

class MemorySigner:
    def __init__(self, private_key_pem: str = None):
        if private_key_pem:
            self.private_key = serialization.load_pem_private_key(private_key_pem.encode(), password=None)
        else:
            self.private_key = ec.generate_private_key(ec.SECP256R1())
        self.public_key = self.private_key.public_key()

    def sign(self, data: str) -> str:
        signature = self.private_key.sign(data.encode(), ec.ECDSA(hashes.SHA256()))
        return base64.b64encode(signature).decode()

    def verify(self, data: str, signature_b64: str, public_key_pem: str = None) -> bool:
        try:
            if public_key_pem:
                pub_key = serialization.load_pem_public_key(public_key_pem.encode())
            else:
                pub_key = self.public_key
            signature = base64.b64decode(signature_b64)
            pub_key.verify(signature, data.encode(), ec.ECDSA(hashes.SHA256()))
            return True
        except InvalidSignature:
            return False
        except Exception:
            return False

    def get_public_key_pem(self) -> str:
        return self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode()
