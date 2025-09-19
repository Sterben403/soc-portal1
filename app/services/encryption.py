import os
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from typing import Optional

class FileEncryption:
    """Service for encrypting and decrypting file attachments using AES-GCM."""
    
    def __init__(self, encryption_key: Optional[str] = None):
        """Initialize with encryption key from environment or generate one."""
        if encryption_key:
            self.key = self._derive_key(encryption_key.encode())
        else:
            # Fallback to environment variable
            env_key = os.getenv("ENCRYPTION_KEY")
            if not env_key:
                raise ValueError("ENCRYPTION_KEY environment variable is required")
            self.key = self._derive_key(env_key.encode())
    
    def _derive_key(self, password: bytes) -> bytes:
        """Derive a 32-byte key from password using PBKDF2."""
        salt = b"soc_portal_salt"  # In production, use unique salt per file
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return kdf.derive(password)
    
    def encrypt_file(self, file_data: bytes) -> bytes:
        """Encrypt file data using AES-GCM."""
        aesgcm = AESGCM(self.key)
        nonce = os.urandom(12)  # 96-bit nonce for AES-GCM
        ciphertext = aesgcm.encrypt(nonce, file_data, None)
        # Return nonce + ciphertext for storage
        return nonce + ciphertext
    
    def decrypt_file(self, encrypted_data: bytes) -> bytes:
        """Decrypt file data using AES-GCM."""
        if len(encrypted_data) < 12:
            raise ValueError("Invalid encrypted data")
        
        nonce = encrypted_data[:12]
        ciphertext = encrypted_data[12:]
        
        aesgcm = AESGCM(self.key)
        return aesgcm.decrypt(nonce, ciphertext, None)
    
    def encrypt_filename(self, filename: str) -> str:
        """Encrypt filename for secure storage."""
        aesgcm = AESGCM(self.key)
        nonce = os.urandom(12)
        ciphertext = aesgcm.encrypt(nonce, filename.encode(), None)
        # Return base64 encoded nonce + ciphertext
        return base64.urlsafe_b64encode(nonce + ciphertext).decode()
    
    def decrypt_filename(self, encrypted_filename: str) -> str:
        """Decrypt filename from secure storage."""
        try:
            encrypted_data = base64.urlsafe_b64decode(encrypted_filename.encode())
            if len(encrypted_data) < 12:
                raise ValueError("Invalid encrypted filename")
            
            nonce = encrypted_data[:12]
            ciphertext = encrypted_data[12:]
            
            aesgcm = AESGCM(self.key)
            return aesgcm.decrypt(nonce, ciphertext, None).decode()
        except Exception as e:
            raise ValueError(f"Failed to decrypt filename: {e}")

# Global encryption service instance
encryption_service = FileEncryption()






