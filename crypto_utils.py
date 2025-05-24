import os
import hashlib
import base64
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.exceptions import InvalidSignature

class RSACrypto:
    @staticmethod
    def generate_key_pair():
        """Generate RSA key pair (2048 bits)"""
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        public_key = private_key.public_key()
        
        # Serialize keys to PEM format
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        return private_pem.decode('utf-8'), public_pem.decode('utf-8')
    
    @staticmethod
    def calculate_file_hash(file_path):
        """Calculate SHA-256 hash of a file"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            # Read file in chunks to handle large files
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    
    @staticmethod
    def sign_file_hash(file_hash, private_key_pem):
        """Sign file hash with RSA private key"""
        try:
            # Load private key
            private_key = serialization.load_pem_private_key(
                private_key_pem.encode('utf-8'),
                password=None
            )
            
            # Sign the hash
            signature = private_key.sign(
                file_hash.encode('utf-8'),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            # Return base64 encoded signature
            return base64.b64encode(signature).decode('utf-8')
        except Exception as e:
            raise Exception(f"Signing failed: {str(e)}")
    
    @staticmethod
    def verify_signature(file_hash, signature_b64, public_key_pem):
        """Verify file signature with RSA public key"""
        try:
            # Load public key
            public_key = serialization.load_pem_public_key(
                public_key_pem.encode('utf-8')
            )
            
            # Decode signature
            signature = base64.b64decode(signature_b64.encode('utf-8'))
            
            # Verify signature
            public_key.verify(
                signature,
                file_hash.encode('utf-8'),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except InvalidSignature:
            return False
        except Exception as e:
            raise Exception(f"Verification failed: {str(e)}")

class FileManager:
    @staticmethod
    def save_uploaded_file(file, upload_folder):
        """Save uploaded file securely"""
        if not file or not file.filename:
            raise ValueError("No file provided")
        
        # Generate secure filename
        filename = FileManager.secure_filename(file.filename)
        file_path = os.path.join(upload_folder, filename)
        
        # Ensure unique filename
        counter = 1
        base_name, ext = os.path.splitext(filename)
        while os.path.exists(file_path):
            filename = f"{base_name}_{counter}{ext}"
            file_path = os.path.join(upload_folder, filename)
            counter += 1
        
        # Save file
        file.save(file_path)
        return filename, file_path
    
    @staticmethod
    def secure_filename(filename):
        """Create secure filename"""
        # Remove directory path
        filename = os.path.basename(filename)
        
        # Replace dangerous characters
        import re
        filename = re.sub(r'[^\w\-_\.]', '_', filename)
        
        # Limit length
        if len(filename) > 255:
            name, ext = os.path.splitext(filename)
            filename = name[:255-len(ext)] + ext
        
        return filename
    
    @staticmethod
    def get_file_size(file_path):
        """Get file size in bytes"""
        return os.path.getsize(file_path)
    
    @staticmethod
    def delete_file(file_path):
        """Delete file safely"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
        except Exception as e:
            print(f"Error deleting file: {e}")
        return False
