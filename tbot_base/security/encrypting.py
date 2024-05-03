import base64
import binascii
import json
import os

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from orjson import orjson
from pydantic import SecretStr


class EncryptManagerError(Exception):
    pass


class EncodeExceptionError(EncryptManagerError):
    pass


class DecodeExceptionError(EncryptManagerError):
    pass


class EncryptManager:
    """
    Strings encrypting/decrypting
    """

    def __init__(self, secret_key: SecretStr):
        """
        secret_key: str - hexadecimal digits only
        """
        self._secret_key: bytes = secret_key.get_secret_value().encode()

    def encrypt_key(self, data: str) -> str:
        return self._encrypt_key(data=data)

    def _encrypt_key(self, data: str) -> str:
        try:
            padder = padding.PKCS7(128).padder()

            data_to_encrypt = (
                padder.update(base64.b64encode(data.encode("utf-8")))
                + padder.finalize()
            )
            key = binascii.unhexlify(self._secret_key)
            iv = os.urandom(16)

            cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
            encryptor = cipher.encryptor()
            encrypted_data = encryptor.update(data_to_encrypt) + encryptor.finalize()

            iv_64 = base64.b64encode(iv).decode("utf-8")
            encrypted_64 = base64.b64encode(encrypted_data).decode("utf-8")

            json_data = {"iv": iv_64, "data": encrypted_64}

            return base64.b64encode(orjson.dumps(json_data)).decode("utf-8")
        except (TypeError, UnicodeEncodeError, binascii.Error) as e:
            # logger.error("{} {}, error {}", err_message, data, error)
            raise EncodeExceptionError("Failed encode key.") from e

    def decrypt_key(self, data: str) -> str:
        return self._decrypt_key(data=data)

    def _decrypt_key(self, data: str) -> str:
        try:
            encrypted = json.loads(base64.b64decode(data).decode("utf-8"))

            encrypted_data = base64.b64decode(encrypted["data"])
            iv = base64.b64decode(encrypted["iv"])

            key = binascii.unhexlify(self._secret_key)

            cipher = Cipher(
                algorithms.AES(key), modes.CBC(iv), backend=default_backend()
            )
            decryptor = cipher.decryptor()

            decrypt_data = decryptor.update(encrypted_data) + decryptor.finalize()
            return base64.b64decode(decrypt_data).decode("utf-8")
        except (
            TypeError,
            UnicodeDecodeError,
            binascii.Error,
            json.JSONDecodeError,
        ) as e:
            raise DecodeExceptionError(
                "Failed decode key. Seems credentials is not valid!"
            ) from e
