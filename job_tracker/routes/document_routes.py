from flask import Blueprint, request, redirect, url_for, flash, send_from_directory, jsonify, current_app
import os

# Set up directories
BASE_UPLOAD = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'uploads')
COVER_LETTERS_DIR = os.path.join(BASE_UPLOAD, 'cover_letters')
OTHER_DOCS_DIR = os.path.join(BASE_UPLOAD, 'other_docs')
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt'}

os.makedirs(COVER_LETTERS_DIR, exist_ok=True)
os.makedirs(OTHER_DOCS_DIR, exist_ok=True)

document_bp = Blueprint('document', __name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@document_bp.route('/documents/upload/<doc_type>', methods=['POST'])
def upload_document(doc_type):
    if 'document' not in request.files:
        flash('No file part', 'danger')
        return redirect(url_for('main.dashboard'))
    file = request.files['document']
    if file.filename == '':
        flash('No selected file', 'danger')
        return redirect(url_for('main.dashboard'))
    if file and allowed_file(file.filename):
        save_dir = COVER_LETTERS_DIR if doc_type == 'cover_letter' else OTHER_DOCS_DIR
        filename = file.filename
        file.save(os.path.join(save_dir, filename))
        flash(f'{doc_type.replace("_", " ").title()} uploaded successfully!', 'success')
    else:
        flash('Invalid file type.', 'danger')

    return redirect(url_for('main.dashboard'))

@document_bp.route('/documents/list/<doc_type>')
def list_documents(doc_type):
    dir_path = COVER_LETTERS_DIR if doc_type == 'cover_letter' else OTHER_DOCS_DIR
    files = os.listdir(dir_path)
    return jsonify(files)

@document_bp.route('/documents/download/<doc_type>/<filename>')
def download_document(doc_type, filename):
    dir_path = COVER_LETTERS_DIR if doc_type == 'cover_letter' else OTHER_DOCS_DIR
    return send_from_directory(dir_path, filename, as_attachment=True)

@document_bp.route('/documents/delete/<doc_type>/<filename>', methods=['POST'])
def delete_document(doc_type, filename):
    dir_path = COVER_LETTERS_DIR if doc_type == 'cover_letter' else OTHER_DOCS_DIR
    try:
        os.remove(os.path.join(dir_path, filename))
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@document_bp.route('/upload_document/<doc_type>', methods=['POST'])
def upload_document_new(doc_type):
    # Handle file upload logic here
    # file = request.files['file']
    # Save file, process doc_type, etc.
    return redirect(url_for('main.dashboard'))
