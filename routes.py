import os
import uuid
from datetime import datetime
from flask import render_template, request, redirect, url_for, flash, session, send_file, jsonify
from werkzeug.utils import secure_filename
from app import app, db
from models import User, FileRecord
from crypto_utils import RSACrypto, FileManager

@app.route('/')
def index():
    """Main dashboard with new beautiful interface"""
    return render_template('index_new.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login/registration"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        
        if not username:
            flash('Username is required', 'error')
            return redirect(url_for('index'))
        
        # Find or create user
        user = User.query.filter_by(username=username).first()
        if not user:
            user = User(username=username)
            db.session.add(user)
            db.session.commit()
            flash(f'New user created: {username}', 'success')
        else:
            flash(f'Welcome back, {username}!', 'success')
        
        session['user_id'] = user.id
        return redirect(url_for('index'))
    
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    """User logout"""
    session.pop('user_id', None)
    flash('Logged out successfully', 'info')
    return redirect(url_for('index'))

@app.route('/keys')
def keys():
    """Key management page"""
    # Get or create default user
    user = User.query.first()
    if not user:
        user = User(username='default_user')
        db.session.add(user)
        db.session.commit()
    
    return render_template('keys.html', user=user)

@app.route('/generate_keys', methods=['POST'])
def generate_keys():
    """Generate new RSA key pair"""
    # Get or create default user
    user = User.query.first()
    if not user:
        user = User(username='default_user')
        db.session.add(user)
        db.session.commit()
    
    try:
        private_key, public_key = RSACrypto.generate_key_pair()
        
        user.private_key = private_key
        user.public_key = public_key
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Khóa RSA mới đã được tạo thành công!',
            'has_keys': True
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Lỗi tạo khóa: {str(e)}'
        }), 500

@app.route('/upload')
def upload_page():
    """File upload page"""
    # Create or get default user
    user = User.query.first()
    if not user:
        user = User(username='default_user')
        db.session.add(user)
        db.session.commit()
    
    return render_template('upload.html', user=user)

@app.route('/upload_file', methods=['POST'])
def upload_file():
    """Handle file upload and signing"""
    # Get or create default user
    user = User.query.first()
    if not user:
        user = User(username='default_user')
        db.session.add(user)
        db.session.commit()
    
    if 'file' not in request.files:
        flash('No file selected', 'error')
        return redirect(url_for('upload_page'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('upload_page'))
    
    try:
        # Save file
        filename, file_path = FileManager.save_uploaded_file(file, app.config['UPLOAD_FOLDER'])
        file_size = FileManager.get_file_size(file_path)
        
        # Calculate file hash
        file_hash = RSACrypto.calculate_file_hash(file_path)
        
        # Sign file if user has private key
        signature = None
        signature_verified = False
        
        if user.private_key and user.public_key:
            try:
                signature = RSACrypto.sign_file_hash(file_hash, user.private_key)
                signature_verified = True
                flash('File đã được tải lên và ký số thành công!', 'success')
            except Exception as e:
                flash(f'File đã được tải lên nhưng ký số thất bại: {str(e)}', 'warning')
        else:
            flash('File đã được tải lên nhưng chưa được ký số (chưa có khóa RSA). Hãy tạo khóa RSA để ký số file.', 'warning')
        
        # Save file record
        file_record = FileRecord(
            filename=filename,
            original_filename=file.filename,
            file_path=file_path,
            file_size=file_size,
            file_hash=file_hash,
            signature=signature,
            signature_verified=signature_verified,
            user_id=user.id
        )
        
        db.session.add(file_record)
        db.session.commit()
        
    except Exception as e:
        flash(f'Upload failed: {str(e)}', 'error')
    
    return redirect(url_for('files'))

@app.route('/files')
def files():
    """File management page"""
    # Get or create default user
    user = User.query.first()
    if not user:
        user = User(username='default_user')
        db.session.add(user)
        db.session.commit()
    
    user_files = FileRecord.query.filter_by(user_id=user.id).order_by(FileRecord.uploaded_at.desc()).all()
    
    # Add warning flash message if user has no keys
    if not user.private_key or not user.public_key:
        flash('Bạn chưa có khóa RSA. Vui lòng tạo khóa để ký số các file.', 'warning')
    
    return render_template('files.html', user=user, files=user_files)

@app.route('/download/<int:file_id>')
def download_file(file_id):
    """Download file with signature verification"""
    # Get default user
    user = User.query.first()
    if not user:
        flash('No user found', 'error')
        return redirect(url_for('upload_page'))
    
    file_record = FileRecord.query.filter_by(id=file_id, user_id=user.id).first()
    if not file_record:
        flash('File not found', 'error')
        return redirect(url_for('files'))
    
    if not os.path.exists(file_record.file_path):
        flash('File no longer exists on disk', 'error')
        return redirect(url_for('files'))
    
    # Verify signature if available
    if file_record.signature:
        if user.public_key:
            try:
                # Recalculate file hash
                current_hash = RSACrypto.calculate_file_hash(file_record.file_path)
                
                # Check if file has been modified
                if current_hash != file_record.file_hash:
                    flash('Warning: File has been modified since upload!', 'error')
                else:
                    # Verify signature
                    is_valid = RSACrypto.verify_signature(
                        file_record.file_hash, 
                        file_record.signature, 
                        user.public_key
                    )
                    
                    if is_valid:
                        flash('File signature verified successfully!', 'success')
                    else:
                        flash('Warning: Invalid file signature!', 'error')
            except Exception as e:
                flash(f'Signature verification failed: {str(e)}', 'error')
    
    return send_file(
        file_record.file_path,
        as_attachment=True,
        download_name=file_record.original_filename
    )

@app.route('/verify/<int:file_id>')
def verify_file(file_id):
    """Verify file signature"""
    # Get default user
    user = User.query.first()
    if not user:
        return jsonify({'error': 'No user found'}), 404
    
    file_record = FileRecord.query.filter_by(id=file_id, user_id=user.id).first()
    if not file_record:
        return jsonify({'error': 'File not found'}), 404
    
    if not file_record.signature:
        return jsonify({'status': 'no_signature', 'message': 'File has no signature'})
    
    if not user.public_key:
        return jsonify({'status': 'no_key', 'message': 'No public key available'})
    
    try:
        # Check if file still exists
        if not os.path.exists(file_record.file_path):
            return jsonify({'status': 'error', 'message': 'File no longer exists'})
        
        # Recalculate hash
        current_hash = RSACrypto.calculate_file_hash(file_record.file_path)
        
        # Check if file modified
        if current_hash != file_record.file_hash:
            return jsonify({'status': 'modified', 'message': 'File has been modified since upload'})
        
        # Verify signature
        is_valid = RSACrypto.verify_signature(
            file_record.file_hash,
            file_record.signature,
            user.public_key
        )
        
        if is_valid:
            return jsonify({'status': 'valid', 'message': 'Signature is valid'})
        else:
            return jsonify({'status': 'invalid', 'message': 'Invalid signature'})
            
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Verification failed: {str(e)}'})

@app.route('/delete/<int:file_id>', methods=['POST'])
def delete_file(file_id):
    """Delete file"""
    # Get default user
    user = User.query.first()
    if not user:
        flash('No user found', 'error')
        return redirect(url_for('upload_page'))
    
    file_record = FileRecord.query.filter_by(id=file_id, user_id=user.id).first()
    if not file_record:
        flash('File not found', 'error')
        return redirect(url_for('files'))
    
    try:
        # Delete file from disk
        FileManager.delete_file(file_record.file_path)
        
        # Delete record from database
        db.session.delete(file_record)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Đã xóa file thành công!'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Lỗi xóa file: {str(e)}'}), 500

@app.route('/check_keys_status')
def check_keys_status():
    """Check if RSA keys exist"""
    user = User.query.first()
    if not user:
        return jsonify({'has_keys': False, 'message': 'Chưa có khóa RSA'})
    
    has_keys = bool(user.private_key and user.public_key)
    return jsonify({
        'has_keys': has_keys,
        'message': 'Đã có khóa RSA' if has_keys else 'Chưa có khóa RSA'
    })

@app.route('/files_api')
def files_api():
    """API endpoint to get files list for the new interface"""
    # Get or create default user
    user = User.query.first()
    if not user:
        user = User(username='default_user')
        db.session.add(user)
        db.session.commit()
    
    user_files = FileRecord.query.filter_by(user_id=user.id).order_by(FileRecord.uploaded_at.desc()).all()
    
    files_data = []
    for file in user_files:
        files_data.append({
            'id': file.id,
            'name': file.original_filename,
            'size': file.file_size,
            'uploaded_at': file.uploaded_at.strftime('%Y-%m-%d %H:%M'),
            'has_signature': bool(file.signature)
        })
    
    return jsonify(files_data)

# Connection management
connection_requests = []
connection_responses = {}

@app.route('/request_connection', methods=['POST'])
def request_connection():
    """Send connection request to receiver"""
    data = request.get_json()
    receiver_ip = data.get('receiver_ip')
    
    if not receiver_ip:
        return jsonify({'success': False, 'error': 'Missing receiver IP'})
    
    # Generate unique request ID
    request_id = str(uuid.uuid4())
    
    # Store connection request (in real app, this would be sent to the receiver)
    connection_request = {
        'id': request_id,
        'sender_ip': request.remote_addr or '127.0.0.1',
        'receiver_ip': receiver_ip,
        'timestamp': datetime.utcnow(),
        'status': 'pending'
    }
    
    connection_requests.append(connection_request)
    
    return jsonify({'success': True, 'request_id': request_id})

@app.route('/check_connection_requests')
def check_connection_requests():
    """Check for pending connection requests"""
    # Filter pending requests for this IP
    current_ip = request.remote_addr or '127.0.0.1'
    
    # In a real app, you'd filter by receiver_ip matching current user's IP
    # For demo, we'll show all pending requests
    pending_requests = [
        req for req in connection_requests 
        if req['status'] == 'pending'
    ]
    
    return jsonify({'requests': pending_requests})

@app.route('/respond_connection', methods=['POST'])
def respond_connection():
    """Respond to connection request (accept/reject)"""
    data = request.get_json()
    request_id = data.get('request_id')
    action = data.get('action')  # 'accept' or 'reject'
    
    if not request_id or action not in ['accept', 'reject']:
        return jsonify({'success': False, 'error': 'Invalid request'})
    
    # Find and update the request
    for req in connection_requests:
        if req['id'] == request_id:
            req['status'] = 'accepted' if action == 'accept' else 'rejected'
            connection_responses[request_id] = action
            break
    
    return jsonify({'success': True})

@app.route('/connection_status')
def connection_status():
    """Check status of connection request"""
    # In a real app, this would check the specific request
    # For demo, we'll return the latest response
    if connection_responses:
        latest_response = list(connection_responses.values())[-1]
        return jsonify({'status': 'accepted' if latest_response == 'accept' else 'rejected'})
    
    return jsonify({'status': 'pending'})

@app.route('/get_my_ip')
def get_my_ip():
    """Get current IP address"""
    # Try to get real IP from headers (for production)
    ip = request.headers.get('X-Forwarded-For', request.headers.get('X-Real-IP', request.remote_addr))
    
    # If behind proxy, get first IP
    if ip and ',' in ip:
        ip = ip.split(',')[0].strip()
    
    # Fallback for local development
    if not ip or ip == '127.0.0.1':
        import socket
        try:
            # Get local network IP
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                ip = s.getsockname()[0]
        except:
            ip = '127.0.0.1'
    
    return jsonify({'ip': ip})

@app.route('/notify_file_received', methods=['POST'])
def notify_file_received():
    """Notify about file received"""
    data = request.get_json()
    file_name = data.get('file_name')
    file_size = data.get('file_size')
    
    # In a real app, this would notify the receiver
    # For now, just return success
    return jsonify({'success': True})

# Global transfer status storage (in production, use Redis or database)
transfer_status = {}

@app.route('/start_file_transfer', methods=['POST'])
def start_file_transfer():
    """Start file transfer notification"""
    data = request.get_json()
    file_name = data.get('file_name')
    file_size = data.get('file_size')
    
    transfer_status['current'] = {
        'status': 'receiving',
        'file_name': file_name,
        'file_size': file_size,
        'progress': 0
    }
    
    return jsonify({'success': True})

@app.route('/update_transfer_progress', methods=['POST'])
def update_transfer_progress():
    """Update transfer progress"""
    data = request.get_json()
    file_name = data.get('file_name')
    progress = data.get('progress')
    
    if 'current' in transfer_status:
        transfer_status['current']['progress'] = progress
    
    return jsonify({'success': True})

@app.route('/complete_file_transfer', methods=['POST'])
def complete_file_transfer():
    """Complete file transfer"""
    data = request.get_json()
    file_name = data.get('file_name')
    file_size = data.get('file_size')
    
    transfer_status['current'] = {
        'status': 'completed',
        'file_name': file_name,
        'file_size': file_size,
        'progress': 100
    }
    
    # Clear status after a short delay
    import threading
    def clear_status():
        import time
        time.sleep(3)
        if 'current' in transfer_status:
            del transfer_status['current']
    
    threading.Thread(target=clear_status).start()
    
    return jsonify({'success': True})

@app.route('/check_transfer_status')
def check_transfer_status():
    """Check current transfer status"""
    if 'current' in transfer_status:
        return jsonify(transfer_status['current'])
    else:
        return jsonify({'status': 'none'})
