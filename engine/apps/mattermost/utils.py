import jwt
from typing import Tuple

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

from apps.mattermost import constants

def verify_mattermost_jwt_signature(token: str, secret: str):
    jwt.decode(token, secret, audience=constants.MATTERMOST_JWT_AUDIENCE, algorithms=[constants.MATTERMOST_JWT_ALGORITHM])

def generate_mattermost_jwt_token(kid: str, private_key: str) -> str:
    payload = {"iss": constants.MATTERMOST_JWT_ISSUER,"aud":constants.MATTERMOST_JWT_AUDIENCE}
    headers = {"kid": kid}
    return jwt.encode(payload, private_key, algorithm=constants.MATTERMOST_JWT_ALGORITHM, headers=headers)


def generate_jwt_rsa_keys() -> Tuple[str, str]:
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=constants.MATTERMOST_RSA_PRIVATE_KEY_SIZE,
        backend=default_backend()
    )

    # Get the public key in OpenSSH format
    public_key = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.OpenSSH,
        format=serialization.PublicFormat.OpenSSH
    ).decode('utf-8')

    # Get the private key in PEM format
    private_key_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ).decode('utf-8')

    return public_key, private_key_pem