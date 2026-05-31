import base64
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from app.core.config import get_settings


def encrypt_api_key(plain_text: str) -> str:
    """
    Encrypts a string using AES-256-GCM.
    Returns format: base64(iv):base64(ciphertext+tag)
    """
    settings = get_settings()
    # Key must be exactly 32 bytes for AES-256
    key = settings.encryption_secret.encode("utf-8")[:32].ljust(32, b'\0')
    
    aesgcm = AESGCM(key)
    iv = os.urandom(12)
    
    cipher_text = aesgcm.encrypt(iv, plain_text.encode("utf-8"), None)
    
    encoded_iv = base64.b64encode(iv).decode("utf-8")
    encoded_cipher = base64.b64encode(cipher_text).decode("utf-8")
    
    return f"{encoded_iv}:{encoded_cipher}"


def decrypt_api_key(encrypted_payload: str) -> str:
    """
    Decrypts an AES-256-GCM encrypted string.
    Expects format: base64(iv):base64(ciphertext+tag)
    """
    if not encrypted_payload or ":" not in encrypted_payload:
        raise ValueError("Invalid encrypted payload format")
        
    encoded_iv, encoded_cipher = encrypted_payload.split(":", 1)
    
    iv = base64.b64decode(encoded_iv)
    cipher_text = base64.b64decode(encoded_cipher)
    
    settings = get_settings()
    key = settings.encryption_secret.encode("utf-8")[:32].ljust(32, b'\0')
    
    aesgcm = AESGCM(key)
    plain_text = aesgcm.decrypt(iv, cipher_text, None)
    
    return plain_text.decode("utf-8")
