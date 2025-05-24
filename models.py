from app import db
from datetime import datetime
from sqlalchemy import Text

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    public_key = db.Column(Text, nullable=True)
    private_key = db.Column(Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with files
    files = db.relationship('FileRecord', backref='owner', lazy=True, cascade='all, delete-orphan')

class FileRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    file_hash = db.Column(db.String(64), nullable=False)  # SHA-256 hash
    signature = db.Column(Text, nullable=True)  # RSA signature
    signature_verified = db.Column(db.Boolean, default=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign key to user
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    def __repr__(self):
        return f'<FileRecord {self.original_filename}>'
